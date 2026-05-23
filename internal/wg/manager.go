package wg

import (
	"fmt"
	"log/slog"
	"math/big"
	"net"
	"os/exec"
	"strconv"
	"strings"
	"sync"
)

// Manager gestiona la interfaz WireGuard vía el binario wg(8).
type Manager struct {
	iface    string
	endpoint string // "165.140.241.96:64000"
	nextFree *net.IPNet
	mu       sync.Mutex
}

// PeerInput representa un peer nuevo.
type PeerInput struct {
	PublicKey string
	AllowedIP string // "10.66.66.5/32"
	Endpoint  string // "165.140.241.96:64000"
	PSK       string
}

// PeerInfo tráfico de un peer.
type PeerInfo struct {
	PublicKey string
	Rx        uint64
	Tx        uint64
}

// NewManager crea el Manager; valida que el binario wg esté presente.
func NewManager(iface, cidr, endpoint string) (*Manager, error) {
	if _, err := exec.LookPath("wg"); err != nil {
		return nil, fmt.Errorf("wireguard-tools no encontrado en PATH: %w", err)
	}
	_, ipnet, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, err
	}
	return &Manager{iface: iface, endpoint: endpoint, nextFree: ipnet}, nil
}

// ─── AddPeer ──────────────────────────────────────────────────────────────────
func (m *Manager) AddPeer(in PeerInput) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Insertar o actualizar peer via wg set
	args := []string{
		"set", m.iface,
		"peer", in.PublicKey,
		"allowed-ips", in.AllowedIP,
	}
	if in.PSK != "" {
		args = append(args, "preshared-key", "/dev/stdin")
		cmd := exec.Command("wg", args...)
		cmd.Stdin = strings.NewReader(in.PSK)
		cmd.Stdout, cmd.Stderr = new(strings.Builder), new(strings.Builder)

		slog.Debug("wg addpeer psks",
			"public_key", in.PublicKey[:8], "allowed_ip", in.AllowedIP)
		return runCmd(cmd)
	}

	if in.Endpoint != "" {
		args = append(args, "endpoint", in.Endpoint)
	}

	cmd := exec.Command("wg", args...)
	cmd.Stdout, cmd.Stderr = new(strings.Builder), new(strings.Builder)

	slog.Debug("wg addpeer native",
		"public_key", in.PublicKey[:8], "allowed_ip", in.AllowedIP, "endpoint", in.Endpoint)
	return runCmd(cmd)
}

// ─── RemovePeer ───────────────────────────────────────────────────────────────
func (m *Manager) RemovePeer(pubKey string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	cmd := exec.Command("wg", "set", m.iface, "peer", pubKey, "remove")
	cmd.Stdout, cmd.Stderr = new(strings.Builder), new(strings.Builder)

	slog.Debug("wg removepeer", "public_key", pubKey[:8])
	return runCmd(cmd)
}

// ─── DevicePeers ───────────────────────────────────────────────────────────────
func (m *Manager) DevicePeers() ([]PeerInfo, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	cmd := exec.Command("wg", "show", m.iface, "transfer")
	out, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("wg show transfer: %w", err)
	}

	return parseWgShow(string(out)), nil
}

// parseWgShow parsea la salida de 'wg show <iface> transfer': cada línea es pubkey<TAB>rx_bytes<TAB>tx_bytes
func parseWgShow(s string) []PeerInfo {
	lines := strings.Split(s, "\n")
	var peers []PeerInfo
	for _, l := range lines {
		l = strings.TrimSpace(l)
		if l == "" {
			continue
		}
		fields := strings.Fields(l)
		if len(fields) < 3 {
			continue
		}
		pk := fields[0]
		rx, err1 := strconv.ParseUint(fields[1], 10, 64)
		tx, err2 := strconv.ParseUint(fields[2], 10, 64)
		if err1 != nil || err2 != nil {
			continue
		}
		peers = append(peers, PeerInfo{PublicKey: pk, Rx: rx, Tx: tx})
	}
	return peers
}

// ─── NextFreeIP ────────────────────────────────────────────────────────────────
func (m *Manager) NextFreeIP(existing map[string]bool) (net.IP, error) {
	base := m.nextFree.IP.To4()
	_, bits := m.nextFree.Mask.Size()
	hostBits := 32 - bits

	for i := 2; i < (1<<hostBits)-1; i++ {
		cand := incrementIP(base.To4(), i)
		if !existing[cand.String()] {
			return cand, nil
		}
	}
	return nil, fmt.Errorf("no free IP in %s", m.nextFree.String())
}

func incrementIP(base net.IP, offset int) net.IP {
	ip4 := base.To4()
	if ip4 == nil {
		return base
	}
	val := new(big.Int).SetBytes(ip4)
	val.Add(val, big.NewInt(int64(offset)))
	b := val.Bytes()
	out := make([]byte, 4)
	copy(out[4-len(b):], b)
	return net.IP(out)
}

// ─── GenerateKeyPair ───────────────────────────────────────────────────────────
// Devuelve clave pública y privada en formato hexadecimal (64 chars cada una).
// Compatible con wg(8) set y wg-quick.
func GenerateKeyPair() (pub string, priv string, err error) {
	// usar el binario wg para generar las claves
	privCmd := exec.Command("wg", "genkey")
	privOut, err := privCmd.Output()
	if err != nil {
		return "", "", fmt.Errorf("wg genkey: %w", err)
	}
	priv = strings.TrimSpace(string(privOut))

	// derivar la pública desde la privada
	pubCmd := exec.Command("wg", "pubkey")
	pubCmd.Stdin = strings.NewReader(priv)
	pubOut, err := pubCmd.Output()
	if err != nil {
		return "", "", fmt.Errorf("wg pubkey: %w", err)
	}
	pub = strings.TrimSpace(string(pubOut))

	return pub, priv, nil
}

// ClientConfig es el archivo de configuración WireGuard listo para el cliente.
// PrivateKey es privada (no exportada) — solo se accede vía String() o getters.
type ClientConfig struct {
	privateKey string // NUNCA se expone por JSON; solo visible en el .conf
	Address    string // IP virtual + /mask, ej "10.66.66.5/24"
	DNS        string // ej "10.66.66.1"
	PublicKey  string
	Endpoint   string
	AllowedIPs string // ej "0.0.0.0/0"
	PSK        string
}

// NewClientConfig es el único constructor público de ClientConfig.
func NewClientConfig(privateKey, address, dns, publicKey, endpoint, allowedIPs, psk string) ClientConfig {
	return ClientConfig{
		privateKey: privateKey,
		Address:    address,
		DNS:        dns,
		PublicKey:  publicKey,
		Endpoint:   endpoint,
		AllowedIPs: allowedIPs,
		PSK:        psk,
	}
}

// ClientConf genera el texto .conf listo para que el usuario lo copie o descargue.
func (c ClientConfig) String() string {
	var sb strings.Builder
	if c.privateKey != "" {
		sb.WriteString("[Interface]\n")
		sb.WriteString("PrivateKey = " + c.privateKey + "\n")
		if c.Address != "" {
			sb.WriteString("Address = " + c.Address + "\n")
		}
		if c.DNS != "" {
			sb.WriteString("DNS = " + c.DNS + "\n")
		}
		sb.WriteString("\n")
	}
	sb.WriteString("[Peer]\n")
	sb.WriteString("PublicKey = " + c.PublicKey + "\n")
	if c.PSK != "" {
		sb.WriteString("PresharedKey = " + c.PSK + "\n")
	}
	if c.Endpoint != "" {
		sb.WriteString("Endpoint = " + c.Endpoint + "\n")
	}
	sb.WriteString("AllowedIPs = " + c.AllowedIPs + "\n")
	return sb.String()
}

// ─── runCmd helper ────────────────────────────────────────────────────────────
func runCmd(cmd *exec.Cmd) error {
	out, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("cmd: %s\noutput: %s", err.Error(), string(out))
	}
	slog.Debug("wg command ok", "cmd", strings.Join(cmd.Args, " "))
	return nil
}

package handlers

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"path"
	"strconv"
	"strings"

	"github.com/usipipo/usipipoproxy/internal/wg"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

// DeviceStore extiende AuthStore con todo lo que necesitan los handlers de dispositivos.
type DeviceStore interface {
	AuthStore
	ListDevices(userID int64) ([]models.Device, error)
	GetDeviceByID(deviceID int64) (*models.Device, error)
	DeleteDevice(deviceID int64) error
	GetTrafficSummary(deviceID int64, period string) (*models.TrafficSummary, error)
	GetAllAssignedIPs() (map[string]bool, error)
	CreateDevice(userID int64, name, pubKey, privKey, ip, psk string) (*models.Device, error)
	GetDeviceByPublicKey(pubKey string) (*models.Device, error)
}

type DevicesHandler struct {
	store     DeviceStore
	wgManager *wg.Manager
	endpoint  string
}

func NewDevicesHandler(store DeviceStore, wgMgr *wg.Manager, endpoint string) *DevicesHandler {
	return &DevicesHandler{store: store, wgManager: wgMgr, endpoint: endpoint}
}

// Router despacha por metodo HTTP bajo el prefijo /proxy/devices.
func (h *DevicesHandler) Router(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		if path.Base(r.URL.Path) == "traffic" {
			h.Traffic(w, r)
			return
		}
		if path.Base(r.URL.Path) == "conf" {
			h.ServeConf(w, r)
			return
		}
		h.List(w, r)
	case http.MethodPost:
		h.Create(w, r)
	case http.MethodDelete:
		id := strings.TrimPrefix(r.URL.Path, "/proxy/devices/")
		h.Delete(w, r, id)
	default:
		writeMethodNotAllowed(w)
	}
}

// GET /proxy/devices — lista de dispositivos del usuario autenticado.
// Devuelve []DeviceResponse: entidades de BD limpias, sin ClientConfig.
func (h *DevicesHandler) List(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "unauthenticated")
		return
	}

	devices, err := h.store.ListDevices(uid)
	if err != nil {
		slog.Error("list devices", "uid", uid, "error", err)
		writeError(w, http.StatusInternalServerError, "failed to list devices")
		return
	}
	if devices == nil {
		devices = []models.Device{}
	}

	// Enriquecer con trafico en vivo desde WireGuard
	if h.wgManager != nil {
		if peers, err := h.wgManager.DevicePeers(); err == nil {
			pm := make(map[string]wg.PeerInfo, len(peers))
			for _, p := range peers {
				pm[p.PublicKey] = p
			}
			for i := range devices {
				if p, ok := pm[devices[i].PublicKey]; ok {
					devices[i].BytesRx = p.Rx
					devices[i].BytesTx = p.Tx
				}
			}
		}
	}

	out := make([]models.DeviceResponse, len(devices))
	for i, d := range devices {
		out[i] = deviceResponseFrom(&d)
	}
	writeJSON(w, http.StatusOK, out)
}

// POST /proxy/devices — crea un dispositivo WireGuard completo.
// Conf (clave privada) se devuelve en el DTO de respuesta, nunca se persiste en BD.
func (h *DevicesHandler) Create(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "unauthenticated")
		return
	}

	var req struct {
		Name string `json:"name"`
		PSK  string `json:"psk,omitempty"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid body")
		return
	}
	req.Name = strings.TrimSpace(req.Name)
	if req.Name == "" {
		writeError(w, http.StatusBadRequest, "name required")
		return
	}

	// Generar par de claves WireGuard
	pubKey, privKey, err := wg.GenerateKeyPair()
	if err != nil {
		slog.Error("keygen", "err", err)
		writeError(w, http.StatusInternalServerError, "key generation failed")
		return
	}

	// Asignar IP virtual libre
	taken, _ := h.store.GetAllAssignedIPs()
	freeIP, err := h.wgManager.NextFreeIP(taken)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "no free IP in subnet")
		return
	}
	targetIP := freeIP.String()

	// Anadir peer en WireGuard
	if err := h.wgManager.AddPeer(wg.PeerInput{
		PublicKey: pubKey,
		AllowedIP: targetIP + "/32",
		Endpoint:  h.endpoint,
		PSK:       req.PSK,
	}); err != nil {
		slog.Error("wg add peer", "ip", targetIP, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to add wireguard peer")
		return
	}

	// Guardar en BD (sin Conf — la clave privada NUNCA se expone por API)
	device, err := h.store.CreateDevice(uid, req.Name, pubKey, privKey, targetIP, req.PSK)
	if err != nil {
		slog.Error("db create device", "err", err)
		_ = h.wgManager.RemovePeer(pubKey) // rollback best-effort
		writeError(w, http.StatusInternalServerError, "failed to save device")
		return
	}

	// Construir ClientConfig como DTO de respuesta (unico punto de construccion)
	conf := wg.NewClientConfig(
		privKey,
		targetIP+"/24",
		"10.66.66.1",
		pubKey,
		h.endpoint,
		"0.0.0.0/0",
		req.PSK,
	)

	slog.Info("device provisioned",
		"uid", uid, "device_id", device.ID, "name", req.Name, "ip", targetIP)
	writeJSON(w, http.StatusCreated, models.CreateDeviceResponse{
		Device: deviceResponseFrom(device),
		Conf:   conf,
	})
}

// DELETE /proxy/devices/{id} — revoca un dispositivo.
func (h *DevicesHandler) Delete(w http.ResponseWriter, r *http.Request, idStr string) {
	deviceID, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil || deviceID == 0 {
		writeError(w, http.StatusBadRequest, "invalid device id")
		return
	}

	d, err := h.store.GetDeviceByID(deviceID)
	if err != nil {
		writeError(w, http.StatusNotFound, "device not found")
		return
	}
	uid, ok := userIDFromCtx(r)
	if !ok || uid != d.UserID {
		writeError(w, http.StatusForbidden, "not authorized")
		return
	}

	// Eliminar peer de WireGuard (best-effort: continua aunque falle)
	if h.wgManager != nil {
		if err := h.wgManager.RemovePeer(d.PublicKey); err != nil {
			slog.Warn("wg remove peer", "device_id", deviceID, "err", err)
		}
	}

	// Marcar inactiva en BD
	if err := h.store.DeleteDevice(deviceID); err != nil {
		slog.Error("db delete device", "device_id", deviceID, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to revoke")
		return
	}

	slog.Info("device revoked", "device_id", deviceID, "uid", uid)
	writeJSON(w, http.StatusOK, map[string]any{
		"status": "revoked", "device_id": deviceID, "name": d.Name,
	})
}

// GET /proxy/devices/{id}/traffic — consumo de trafico por periodo.
func (h *DevicesHandler) Traffic(w http.ResponseWriter, r *http.Request) {
	uid, _ := userIDFromCtx(r)
	devID, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil || devID == 0 {
		writeError(w, http.StatusBadRequest, "invalid device id")
		return
	}
	d, err := h.store.GetDeviceByID(devID)
	if err != nil {
		writeError(w, http.StatusNotFound, "device not found")
		return
	}
	if d.UserID != uid {
		writeError(w, http.StatusForbidden, "not authorized")
		return
	}

	period := r.URL.Query().Get("period")
	if period == "" {
		period = "daily"
	}

	sum, err := h.store.GetTrafficSummary(devID, period)
	if err != nil {
		slog.Error("traffic query", "device_id", devID, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to get traffic")
		return
	}
	writeJSON(w, http.StatusOK, sum)
}

// GET /proxy/devices/{id}/conf — devuelve el archivo .conf WireGuard del dispositivo.
// Solo el propietario puede descargarlo.
func (h *DevicesHandler) ServeConf(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "unauthenticated")
		return
	}

	trimmed := strings.TrimPrefix(r.URL.Path, "/")
	idStr := strings.SplitN(trimmed, "/", 2)[0]
	devID, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil || devID == 0 {
		writeError(w, http.StatusBadRequest, "invalid device id")
		return
	}

	d, err := h.store.GetDeviceByID(devID)
	if err != nil {
		writeError(w, http.StatusNotFound, "device not found")
		return
	}
	if d.UserID != uid {
		writeError(w, http.StatusForbidden, "not authorized")
		return
	}
	if d.PrivateKey == "" {
		slog.Warn("conf requested but no private key stored", "device_id", devID)
		writeError(w, http.StatusNotFound, "configuration not available")
		return
	}

	conf := wg.NewClientConfig(
		d.PrivateKey,
		d.AssignedIP+"/24",
		"10.66.66.1",
		d.PublicKey,
		h.endpoint,
		"0.0.0.0/0",
		d.PSK,
	)

	slog.Info("conf served", "uid", uid, "device_id", devID, "name", d.Name)
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Header().Set("Content-Disposition",
		fmt.Sprintf("attachment; filename=\"device-%d.conf\"", devID))
	_, _ = w.Write([]byte(conf.String()))
}

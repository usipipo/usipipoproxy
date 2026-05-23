package handlers

import (
	"crypto/rand"
	"fmt"
)

// genUUIDv4 genera un UUID v4 string sin guiones (para td_wallet_label).
func genUUIDv4() string {
	u := make([]byte, 16)
	rand.Read(u)
	// version 4
	u[6] = (u[6] & 0x0f) | 0x40
	// variant RFC 4122
	u[8] = (u[8] & 0x3f) | 0x80
	return fmt.Sprintf("%08x%04x%04x%04x%012x",
		u[0:4], u[4:6], u[6:8], u[8:10], u[10:])
}

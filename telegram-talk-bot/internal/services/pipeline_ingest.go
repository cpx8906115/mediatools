package services

import (
	"bytes"
	"encoding/json"
	"net/http"
	"strings"
	"time"
)

type PipelineIngestor struct {
	URL    string
	Secret string
	Rules  []string
}

func NewPipelineIngestor(url string, rules string, secret string) *PipelineIngestor {
	var rs []string
	for _, r := range strings.Split(rules, ";") {
		r = strings.TrimSpace(r)
		if r != "" {
			rs = append(rs, r)
		}
	}
	return &PipelineIngestor{URL: url, Secret: secret, Rules: rs}
}

func (p *PipelineIngestor) match(text string) bool {
	if p == nil || len(p.Rules) == 0 {
		return true
	}
	tl := strings.ToLower(text)
	for _, r := range p.Rules {
		rl := strings.ToLower(r)
		if rl == "hasurl" {
			if strings.Contains(tl, "http://") || strings.Contains(tl, "https://") {
				return true
			}
			continue
		}
		if strings.HasPrefix(rl, "prefix:") {
			if strings.HasPrefix(tl, strings.TrimPrefix(rl, "prefix:")) {
				return true
			}
			continue
		}
		if strings.HasPrefix(rl, "contains:") {
			if strings.Contains(tl, strings.TrimPrefix(rl, "contains:")) {
				return true
			}
			continue
		}
		if strings.Contains(tl, rl) {
			return true
		}
	}
	return false
}

func (p *PipelineIngestor) Ingest(payload map[string]any) {
	if p == nil || p.URL == "" {
		return
	}
	text, _ := payload["text"].(string)
	if !p.match(text) {
		return
	}

	b, err := json.Marshal(payload)
	if err != nil {
		return
	}

	client := &http.Client{Timeout: 4 * time.Second}
	req, err := http.NewRequest("POST", p.URL, bytes.NewReader(b))
	if err != nil {
		return
	}
	req.Header.Set("Content-Type", "application/json")
	if p.Secret != "" {
		req.Header.Set("X-Ingest-Secret", p.Secret)
	}
	_, _ = client.Do(req) // best-effort; ignore errors
}

# Optional spike: Official Anthropic Python SDK for first-party Messages API

Status: **not implemented**. This captures the guarded approach aligned with the
architecture plan (`providers-anthropic-sdk-spike`).

## Preconditions

1. Maintain **parity harness tests** comparing an SDK-driven stream versus the
   current `AnthropicMessagesTransport` + `httpx` reference for identical
   client-visible SSE (thinking blocks, tool lifecycles, error mapping snapshots).
2. Gate the SDK path behind **explicit adapter opt-in** (not the default catalog
   path for OpenRouter/Ollama/LM Studio/DeepSeek hosts).

## Implementation sketch

- Add **`anthropic`** dependency only after the parity harness exists.
- Use **`AsyncAnthropic`** streamed message iterators; normalize deltas into the
   same structures `core/anthropic` already expects before emitting SSE strings.
- Keep **`AnthropicMessagesTransport`** generic `httpx` loop for heterogeneous
   Anthropic-shaped gateways; SDK path is **only** for pinned Anthropic-inc
   base URLs/version headers.

Fail closed: if SDK deltas diverge from the Claude Code observability contract,
keep the adapter disabled or revert the spike.

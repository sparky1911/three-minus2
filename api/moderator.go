package main

import "context"

type Verdict struct {
	Decision  string
	Score     float64 // APPROVE | REJECT | REVIEW
	Stage     string
	LatencyMS int64
}

type Moderator interface {
	Moderate(ctx context.Context, text string) (Verdict, error)
}

type StubModerator struct{}

func (StubModerator) Moderate(ctx context.Context, text string) (Verdict, error) {
	return Verdict{Decision: "APPROVE", Score: 0, Stage: "stub"}, nil
}

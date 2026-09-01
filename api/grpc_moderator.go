package main

import (
	"context"
	"time"

	"github.com/you/moderation-demo/api/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type GRPCModerator struct {
	client pb.ModerationClient
}

func NewGRPCModerator(addr string) (*GRPCModerator, error) {
	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}
	return &GRPCModerator{client: pb.NewModerationClient(conn)}, nil
}

func (g *GRPCModerator) Moderate(ctx context.Context, text string) (Verdict, error) {
	ctx, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
	defer cancel()
	start := time.Now()
	res, err := g.client.Moderate(ctx, &pb.ModerateRequest{Text: text})
	if err != nil {
		return Verdict{}, err
	}
	return Verdict{
		Decision:  res.Decision.String(),
		Score:     float64(res.Score),
		Stage:     res.Stage,
		LatencyMS: time.Since(start).Milliseconds(),
	}, nil
}

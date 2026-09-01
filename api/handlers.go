package main

import (
	"database/sql"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type CreateCommentRequest struct {
	AuthorID string `json:"author_id" binding:"required"`
	Text     string `json:"text" binding:"required"`
}

type Comment struct {
	ID        string `json:"id"`
	AuthorID  string `json:"author_id"`
	Text      string `json:"text"`
	Status    string `json:"status"`
	CreatedAt string `json:"created_at"`
}

func CreateComments(db *sql.DB, mod Moderator) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req CreateCommentRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}
		id := uuid.NewString()
		_, err := db.Exec(
			`INSERT INTO comments (id,author_id,text,status) VALUES(?,?,?,?)`, id, req.AuthorID, req.Text, "PENDING",
		)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		v, err := mod.Moderate(c.Request.Context(), req.Text)
		if err != nil {
			log.Printf("moderation failed  for  %s:%v", id, err)
			v = Verdict{Decision: "REVIEW", Stage: "error"}
		}
		if _, err := db.Exec(`UPDATE comments SET status =? WHERE ID=?`, v.Decision, id); err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return

		}
		if _, err := db.Exec(
			`INSERT INTO decisions (comment_id, stage, score, verdict, latency_ms)
			 VALUES (?, ?, ?, ?, ?)`,
			id, v.Stage, v.Score, v.Decision, v.LatencyMS,
		); err != nil {
			log.Printf("audit write failed for %s: %v", id, err)
		}
		c.JSON(201, gin.H{
			"id":        id,
			"author_id": req.AuthorID,
			"text":      req.Text,
			"status":    v.Decision,
			"score":     v.Score,
			"stage":     v.Stage,
		})
	}
}

func listComments(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		rows, err := db.Query(
			`SELECT id, author_id, text, status, created_at
			 FROM comments ORDER BY created_at DESC LIMIT 50`)

		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()
		out := []Comment{}
		for rows.Next() {
			var cm Comment
			if err := rows.Scan(&cm.ID, &cm.AuthorID, &cm.Text, &cm.Status, &cm.CreatedAt); err != nil {
				c.JSON(500, gin.H{"error": err.Error()})
				return
			}
			out = append(out, cm)
		}
		c.JSON(200, out)

	}
}

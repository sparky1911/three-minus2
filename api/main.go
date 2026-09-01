package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	addr := os.Getenv("MODERATION_ADDR")
	if addr == "" {
		addr = "localhost:50051"
	}
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "moderation.db"
	}
	mod, err := NewGRPCModerator(addr)
	db, err := openDB("moderation.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	r := gin.Default()
	mod, err = NewGRPCModerator("localhost:50051")
	if err != nil {
		log.Fatal(err)
	}
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})
	r.POST("/comments", CreateComments(db, mod))
	r.GET("/comments", listComments(db))

	r.Run(":8080")
}

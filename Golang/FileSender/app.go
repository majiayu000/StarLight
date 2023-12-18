package main

import "github.com/gin-gonic/gin"

func main() {
	r := gin.Default()
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})
	r.GET("/local/file", func(c *gin.Context) {

		filePath := "./example.pdf"
		fileName := "example.pdf"
		c.Header("Content-Disposition", "attachment; filename="+fileName)
		c.Header("Content-Type", "application/pdf")
		c.File(filePath)
	})

	r.Run()
}

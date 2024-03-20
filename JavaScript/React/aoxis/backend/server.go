package main

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/rs/cors"
)

type ErrorResponse struct {
	Message string `json:"message"`
}

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/401", handler)
	mux.HandleFunc("/302", redirectHandler)
	mux.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello, you've requested: %s\n", r.URL.Path)
	})

	corsMiddleware := cors.Default().Handler(mux)

	http.ListenAndServe(":8080", corsMiddleware)
}

func handler(w http.ResponseWriter, r *http.Request) {
	if !isLoggedIn(r) {
		response := ErrorResponse{
			Message: "Unauthorized: Please log in.",
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusUnauthorized)
		json.NewEncoder(w).Encode(response)
		return
	}
}

func redirectHandler(w http.ResponseWriter, r *http.Request) {
	if !isLoggedIn(r) {
		response := struct {
			Status int    `json:"status"`
			Key    string `json:"key"`
		}{
			Status: http.StatusFound,
			Key:    "302",
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusFound)
		json.NewEncoder(w).Encode(response)
		fmt.Println("Redirecting...")
	}
}

func isLoggedIn(r *http.Request) bool {

	return false
}

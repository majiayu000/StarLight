package main

import (
	"fmt"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

func main() {

	// if len(os.Args) != 2 {
	// 	fmt.Fprintf(os.Stderr, "Usage: %s <config-file-path>\n",
	// 		os.Args[0])
	// 	os.Exit(1)
	// }

	// configFile := os.Args[1]
	conf := kafka.ConfigMap{
		"bootstrap.servers": "localhost:9092",
		"client.id":         "go-producer",
	}
	conf["group.id"] = "kafka-go-getting-started"
	conf["auto.offset.reset"] = "earliest"

	c, err := kafka.NewConsumer(&conf)

	if err != nil {
		fmt.Printf("Failed to create consumer: %s", err)
		os.Exit(1)
	}

	topic := "purchases"
	err = c.SubscribeTopics([]string{topic}, nil)
	// Set up a channel for handling Ctrl-C, etc
	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	// Process messages
	run := true
	for run {
		select {
		case sig := <-sigchan:
			fmt.Printf("Caught signal %v: terminating\n", sig)
			run = false
		default:
			ev, err := c.ReadMessage(100 * time.Millisecond)
			if err != nil {
				// Errors are informational and automatically handled by the consumer
				continue
			}
			fmt.Printf("Consumed event from topic %s: key = %-10s value = %s\n",
				*ev.TopicPartition.Topic, string(ev.Key), string(ev.Value))
			// parts := strings.Split(string(ev.Value))
			// if len(parts) < 2 {
			// 	fmt.Println("Invalid message format. Skipping.")
			// 	continue
			// }

			// data := parts[0]
			timestampStr := string(ev.Value)

			// Convert the string timestamp to an integer
			sentTimestamp, err := strconv.ParseInt(timestampStr, 10, 64)
			if err != nil {
				fmt.Println("Could not parse timestamp. Skipping.")
				continue
			}

			receivedTimestamp := time.Now().UnixNano() / 1e6 // current time in milliseconds

			latency := receivedTimestamp - sentTimestamp
			fmt.Printf("Consumed event from topic %s: key = %-10s  latency = %d ms\n",
				*ev.TopicPartition.Topic, string(ev.Key), latency)
		}
	}

	c.Close()

}

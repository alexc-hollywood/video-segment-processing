package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"

	"github.com/segmentio/ksuid"
)

const inputVideo = "input_video.avi"
const outputVideo = "output_video.mp4"
const segmentLength = 10
const videoLength = 2 * 60
const numSegments = videoLength / segmentLength

func transcodeSegment(inputFile string, startTime int, segmentLength int, outputSegment string) {
	cmd := exec.Command("ffmpeg", "-y", "-ss", strconv.Itoa(startTime), "-t", strconv.Itoa(segmentLength), "-i", inputFile, "-c:v", "libx265", "-c:a", "aac", outputSegment)
	err := cmd.Run()
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	// Create a buffered channel to control concurrency
	jobs := make(chan int, numSegments)
	var wg sync.WaitGroup

	// Launch worker pool
	for w := 1; w <= 4; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for startTime := range jobs {
				outputSegment := fmt.Sprintf("segment_%s.mp4", ksuid.New().String())
				transcodeSegment(inputVideo, startTime, segmentLength, outputSegment)
				fmt.Printf("Worker %d processed segment starting at %d seconds\n", workerID, startTime)
			}
		}(w)
	}

	// Add tasks to the jobs channel
	for i := 0; i < numSegments; i++ {
		jobs <- i * segmentLength
	}
	close(jobs)

	// Wait for all workers to complete
	wg.Wait()

	// Generate the list of segments
	segments, err := ioutil.ReadDir(".")
	if err != nil {
		log.Fatal(err)
	}

	var segmentFiles []string
	for _, segment := range segments {
		if strings.HasPrefix(segment.Name(), "segment_") && strings.HasSuffix(segment.Name(), ".mp4") {
			segmentFiles = append(segmentFiles, fmt.Sprintf("file '%s'", segment.Name()))
		}
	}

	segmentsList := strings.Join(segmentFiles, "\n")
	ioutil.WriteFile("segments_list.txt", []byte(segmentsList), 0644)

	// Concatenate the segments to create the final video
	cmd := exec.Command("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "segments_list.txt", "-c", "copy", outputVideo)
	err = cmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	// Clean up temporary files
	for _, segment

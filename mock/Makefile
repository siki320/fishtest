GOPATH:=$(CURDIR)
export GOPATH
all: build

fmt:
	gofmt -l -w -s src/

dep:fmt
#go get github.com/garyburd/redigo/redis
#go get code.google.com/p/gcfg
#go get github.com/Shopify/sarama
#go get -d github.com/wvanbergen/kafka
#go get -d github.com/wvanbergen/kazoo-go

test:
	go test -v worker

build:dep
	go build -o bin/api-mock main

output:build
	mkdir -p output
	mkdir -p output/bin
	mkdir -p output/data
	mkdir -p output/conf
	mkdir -p output/log
	mkdir -p output/status
	mkdir -p output/status/stream-canal
	cp -r bin/* output/bin/
	cp -r conf/* output/conf/
	cp output/conf/canal.conf.online output/conf/canal.conf
	cp -r README.md  output/
	cp -r load.sh  output/

clean:
	rm -rf pkg 
	rm -rf bin/canal

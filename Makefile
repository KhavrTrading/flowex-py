.PHONY: build-linux build-mac build-windows build-all package

build-linux:
	CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build -buildmode=c-shared \
		-o flowex/lib/libflowex.so ./cmd/lib

build-mac:
	CGO_ENABLED=1 GOOS=darwin GOARCH=arm64 go build -buildmode=c-shared \
		-o flowex/lib/libflowex.dylib ./cmd/lib

build-windows:
	CGO_ENABLED=1 GOOS=windows GOARCH=amd64 go build -buildmode=c-shared \
		-o flowex/lib/libflowex.dll ./cmd/lib

build-all: build-linux build-mac build-windows

package: build-all
	python -m build

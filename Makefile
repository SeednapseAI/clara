PKG_VERSION := $(shell poetry version | awk '{print $$2}')

release:
	git tag "v$(PKG_VERSION)"
	git push -u origin "v$(PKG_VERSION)"

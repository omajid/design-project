
all:


.PHONY: all stop clean clean-all

clean: stop
	find -iname '*.pyc' | xargs rm -f
	rm -f twistd.log twistd.pid

clean-all: clean
	rm -f user.settings
	rm -rf cache

stop:
	if [ -e twistd.pid ]; then \
		kill $$(cat twistd.pid); \
	fi


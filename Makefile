
all:



clean: stop
	find -iname '*.pyc' | xargs rm -f
	rm -f user.settings
	rm -f twistd.log twistd.pid

stop:
	if [ -e twistd.pid ]; then \
		kill $$(cat twistd.pid); \
	fi

start:
	twistd -y server.tac

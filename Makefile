HOSTNAME=`hostname -s`
CONTAINER=thebaron/flask-skeleton
CONTAINER_TAG=dev-latest

.PHONY: default
default: virtualenv bower_install syncdb collectstatic
	@echo 'Build complete.'

.PHONY: virtualenv
virtualenv:
	@echo Setting up environment
	@. ./env.sh

.PHONY: debugsmtp
debugsmtp:
	python -m smtpd -n -c DebuggingServer localhost:1025

.PHONY: devcelery
devcelery:
	. var/${HOSTNAME}/bin/activate && rabbitmq-server&
	. var/${HOSTNAME}/bin/activate && celery -A flask_skeleton worker -B -l info -Q flask_skeleton -n flask_skeleton.%%n

.PHONY: container
container:
	docker ps || exit -1
	docker build -t ${CONTAINER}:${CONTAINER_TAG}
	docker push

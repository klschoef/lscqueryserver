# Verwende das offizielle MongoDB Image als Basis
FROM mongo:6.0

COPY ssl/mongodb.pem /etc/mongodb.pem
COPY mongod.conf /etc/mongod.conf

CMD ["--config", "/etc/mongod.conf"]
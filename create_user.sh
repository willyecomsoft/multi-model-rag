user=$1
port=$2

if [ -z $port ]; then
  echo "port is empty"
  exit
fi

cp -r uat $1

sed -i "s|uat|$user|" $user/fileEvent.json
sed -i "s|5002|$port|" $user/fileEvent.json

sed -i "s|uat|$user|" $user/contentEvent.json
sed -i "s|5002|$port|" $user/contentEvent.json

sed -i "s|uat|$user|" $user/fts-index.json

sed -i "s|uat|$user" $user/.env
sed -i "s|5002|$port" $user/.env

sed -i "s|uat|$user" $user/start.sh
sed -i "s|5002:|$port:" $user/.env

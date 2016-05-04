#!/bin/bash

#####################################################
#Script to Install the Giotto Machine Learning layer#
#####################################################

service=supervisor

echo 'Please make sure that you have installed BuildingDepot before proceeding forward!!\n'

if [[ $UID -ne 0 ]]; then
        echo -e "\n$0 must be run as root. Most functions require super-user priviledges!\n"
        exit 1
fi

echo -e "\nPlease provide the hostname or IP address of your BuildingDepot installation."
read bd_hostname
sed -i "s|<host_name>|$bd_hostname|g" ./giotto/config/buildingdepot_setting.json
echo -e "Please enter the OAuth id and key generated from your Dataservice (http://<hostname>:82)."
echo -e "OAuth Id:"
read oauth_id
echo -e "OAuth Key:"
read oauth_key
sed -i "s|<oauth_id>|$oauth_id|g" ./giotto/config/buildingdepot_setting.json
sed -i "s|<oauth_key>|$oauth_key|g" ./giotto/config/buildingdepot_setting.json


#Copy code and path to PYTHON PATH
mkdir -p /srv
cp -r giotto/ /srv/
cp supervisor-ml.conf /etc/supervisor/conf.d/
echo 'export PYTHONPATH=${PYTHONPATH}:/srv' >> ~/.bashrc
source ~/.bashrc

function install_packages {

#Install python dependencies
apt-get install python-numpy python-scipy python-sklearn
pip install pymongo==2.8.0
pip install influxdb==2.6.0

}

install_packages
service supervisor stop
echo -e "Please wait!\n"
while (( ($(service supervisor status | grep "is running" | wc -l)) > 0 ));do
    continue
done
service supervisor start

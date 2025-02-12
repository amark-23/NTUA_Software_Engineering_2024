
se2452 logout
read -p "Press any key to continue..."
se2452 login --username admin --passw freepasses4all
read -p "Press any key to continue..."
se2452 healthcheck
read -p "Press any key to continue..."
se2452 resetpasses
read -p "Press any key to continue..."
se2452 healthcheck
read -p "Press any key to continue..."
se2452 resetstations
read -p "Press any key to continue..."
se2452 healthcheck
read -p "Press any key to continue..."
se2452 admin --addpasses --source passes52.csv
read -p "Press any key to continue..."
se2452 healthcheck
read -p "Press any key to continue..."
se2452 tollstationpasses --station AM08 --from 20220110 --to 20220124 --format json
read -p "Press any key to continue..."
se2452 tollstationpasses --station NAO04 --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station NO01 --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station OO03 --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station XXX --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station OO03 --from 20220110 --to 20220124 --format YYY
read -p "Press any key to continue..."
se2452 errorparam --station OO03 --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station AM08 --from 20220111 --to 20220122 --format json
read -p "Press any key to continue..."
se2452 tollstationpasses --station NAO04 --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station NO01 --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station OO03 --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station XXX --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 tollstationpasses --station OO03 --from 20220111 --to 20220122 --format YYY
read -p "Press any key to continue..."
se2452 passanalysis --stationop AM --tagop NAO --from 20220110 --to 20220124 --format json
read -p "Press any key to continue..."
se2452 passanalysis --stationop NAO --tagop AM --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop NO --tagop OO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop OO --tagop KO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop XXX --tagop KO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop AM --tagop NAO --from 20220111 --to 20220122 --format json
read -p "Press any key to continue..."
se2452 passanalysis --stationop NAO --tagop AM --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop NO --tagop OO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop OO --tagop KO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passanalysis --stationop XXX --tagop KO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop AM --tagop NAO --from 20220110 --to 20220124 --format json
read -p "Press any key to continue..."
se2452 passescost --stationop NAO --tagop AM --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop NO --tagop OO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop OO --tagop KO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop XXX --tagop KO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop AM --tagop NAO --from 20220111 --to 20220122 --format json
read -p "Press any key to continue..."
se2452 passescost --stationop NAO --tagop AM --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop NO --tagop OO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop OO --tagop KO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 passescost --stationop XXX --tagop KO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid NAO --from 20220110 --to 20220124 --format json
read -p "Press any key to continue..."
se2452 chargesby --opid GE --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid OO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid KO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid NO --from 20220110 --to 20220124 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid NAO --from 20220111 --to 20220122 --format json
read -p "Press any key to continue..."
se2452 chargesby --opid GE --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid OO --from 20220111 --to 20220122 --format csv
read -p "Press any key to continue..."
se2452 chargesby --opid KO --from 20220111 --to 20220122 --format csv
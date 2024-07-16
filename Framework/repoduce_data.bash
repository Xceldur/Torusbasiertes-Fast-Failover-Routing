#!/bin/bash
# check that script runs as root or with sudo else exit
# [https://stackoverflow.com/questions/18215973/how-to-check-if-running-as-root-in-a-bash-script]
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run this script as root or using sudo!"
  exit 2
fi
# check if temp results exist and prompt user for deletion
TempExpResultPath="/tmp/TempExpResult-22.json"
if [ -f "$TempExpResultPath" ]; then
  read -p "The file $TempExpResultPath exists. Do you want to delete it? (y/n): " answer
  if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm "$TempExpResultPath"
    echo "File deleted."
  else
    echo "File not deleted. Then this script can not be used"
    exit 1
  fi
fi
# check if output folder exists and is empty otherwise it will be created after prompt
FOLDER_PATH="reproduced_data/"
if [ -d "$FOLDER_PATH" ]; then
  if [ "$(ls -A $FOLDER_PATH)" ]; then
    read -r -p "The folder exists and is not empty. Do you want to clear it? (y/n): " answer
    case $answer in
      [Yy]* )
        rm -rf "${FOLDER_PATH:?}"/*
        echo "Folder cleared."
        ;;
      * )
        echo "Folder not cleared. Then this script can not be used"
        exit 1
        ;;
    esac
  fi
else
  mkdir -p "$FOLDER_PATH"
  echo "Output Folder created."
fi

# --- terminal flag handling ---
execute_random_edge=false
execute_random_node=false
execute_cluster_step=false
execute_cluster_nodes=false
execute_towards_dst=false

show_help() {
  echo "This script can be used to reproduce the data form the thesis"
  echo "Usage: $0 [OPTIONS]"
  echo
  echo "Options:"
  echo "  --random_edge       Execute the algorithms on random edge"
  echo "  --random_node       Execute the algorithms on random node"
  echo "  --cluster_step      Execute the algorithms on cluster step"
  echo "  --cluster_node      Execute the algorithms on cluster node"
  echo "  --towards_dst       Execute the algorithms on towards destination "
  echo "  --help              Display this help message"
  echo "Without a flag all failure patterns will be executed"
}

for arg in "$@"; do
  case $arg in
      --random_edge)
          execute_random_edge=true
          ;;
      --random_node)
          execute_random_node=true
          ;;
      --cluster_step)
          execute_cluster_step=true
          ;;
      --cluster_node)
          execute_cluster_nodes=true
          ;;
      --towards_dst)
          execute_towards_dst=true
          ;;
      --help)
          show_help
          exit 0
          ;;
      *)
          echo "Unrecognized option: $arg"
          show_help
          exit 1
          ;;
  esac
done

if [ $# -eq 0 ]; then
  execute_random_edge=true
  execute_random_node=true
  execute_cluster_step=true
  execute_cluster_nodes=true
  execute_towards_dst=true
fi
# --- end terminal flag handling ---

# --- run the framework for each patter and algorithm ---
ALGO_NAMES=("low_stretch" "hamilton" "hamilton_low_stretch")

# function to move the generated file form temp to the result folder

move_result() {
  local algo=$1
  local pattern=$2
  if [ ! -f "${TempExpResultPath}" ]; then
    echo "Error something went wrong: Temp-Result-File does not exist."
    echo "Error on: ALGO: ${algo}; PATTERN: ${pattern}"
    exit 5
  fi
  mv "${TempExpResultPath}" "${FOLDER_PATH}results_${pattern}-${algo}.json"
}

# run mininet clean for the prevention of potential complications
sudo mn -c > /dev/null 2>&1

# random edges
if $execute_random_edge; then
  echo "Random Edges will now be executed"
  sleep 2s
  for algo in "${ALGO_NAMES[@]}"; do
      echo
      python main_cli_randomEdge.py --size_x 5 --size_y 5 "$algo"
      move_result "$algo" "random_edge"
  done
fi
# random nodes
if $execute_random_node; then
  echo "Random Nodes will now be executed"
  sleep 2s
  for algo in "${ALGO_NAMES[@]}"; do
      python main_cli_randomNode.py --size_x 7 --size_y 7 "$algo"
      move_result "$algo" "random_node"
  done
fi
# cluster step
if $execute_cluster_step; then
  echo "Cluster Step will now be executed"
  sleep 2s
  for algo in "${ALGO_NAMES[@]}"; do
      python main_cli_randomEdge.py --size_x 7 --size_y 7 "$algo"
      move_result "$algo" "cluster_step"
  done
fi
# cluster nodes
if $execute_cluster_nodes; then
  echo "Cluster Nodes will now be executed"
  sleep 2s
  for algo in "${ALGO_NAMES[@]}"; do
      python main_cli_randomEdge.py --size_x 7 --size_y 7 "$algo"
      move_result "$algo" "cluster_nodes"
  done
fi
# towards dest.
if $execute_towards_dst; then
  echo "Towards Dest. will now be executed"
  sleep 2s
  for algo in "${ALGO_NAMES[@]}"; do
      python main_cli_twoardsDest.py --size_x 5 --size_y 5 "$algo"
      move_result "$algo" "towards_dst"
  done
fi
#--- end run the framework for each patter and algorithm ---
echo -e "\n\nYou may find the reproduced data in ${FOLDER_PATH}"
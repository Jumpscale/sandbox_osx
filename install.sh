#!/bin/bash

set -e

if [ -z "$HOMEDIR" ] ; then
    export HOMEDIR="$HOME"
fi

if [ -z "$HOMEDIR" ] ; then
    echo "[-] ERROR, could not specify homedir"
    exit 1
fi

if [ "$(uname)" == "Darwin" ]; then
    set +e
    which brew 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        echo "[+] install brew, the must have package manager for OSX."
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
    git -V 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        echo "[+] install git."
        brew install git
    fi
    rsync -h 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        echo "[+] install rsync."
        brew install rsync
    fi
    zip -h 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        echo "[+] install zip."
        brew install zip
    fi
    set -e

elif [ -f /etc/redhat-release ]; then
    dnf update
    dnf install curl git wget -y
elif [ -f /etc/arch-release ]; then
    pacman -S --noconfirm curl git wget
else
    #TODO: *2 need to support windows as well
    sudo apt-get update
    sudo apt-get install curl -y
    sudo apt-get install git wget rsync -y
fi

#if not exist then do in /opt/code...


export ZLogFile='/tmp/zutils.log'

die() {
    echo "ERROR"
    echo "[-] something went wrong: $1"
    cat $ZLogFile
    exit 1
}


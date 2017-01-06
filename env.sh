HOSTNAME=`hostname -s`
ROOTDIR="var/$HOSTNAME"

mkdir -p $ROOTDIR/bin $ROOTDIR/log $ROOTDIR/tmp $ROOTDIR/etc $ROOTDIR/www $ROOTDIR/db $ROOTDIR/log/emails $ROOTDIR/log/celery

# For MacOS X 10.9, when buidling Pillow, the cc uses an invalid
# command line option; this forces XCode to ignore it (at least for now).
#
OS=`uname`
if [ 'x$OS' == 'xDarwin' ]; then
    export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future
fi

# Install bower if it's not in the path
BOWER_BIN=`which bower`
if [ ! -x $BOWER_BIN ]; then
    npm install -g bower
fi

if [ -e $ROOTDIR/bin/activate ]; then
    echo Activating Python virtualenv
    . $ROOTDIR/bin/activate
else
    echo Building out Python virtualenv
    virtualenv --python=python3.5 $ROOTDIR
    echo Activating Python virtualenv
    . $ROOTDIR/bin/activate

    echo Installing required packages...
    easy_install readline

    # Install cython
    pip3 install cython
    # Install cython'ed falcon
    pip3 install --no-binary :all: falcon

fi

pip3 install -q -r requirements.txt




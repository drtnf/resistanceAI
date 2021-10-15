const sio = io({
    transportOptions: {
      polling: {
        extraHeaders: {
          'X-Username': window.location.hash.substring(1)
        }
      }
    }
  });

sio.on('connect', () => {
    console.log("connected.");
    sio.emit('sum', {numbers: [1, 2]}, (result) => {
        console.log(result);
    });
});

sio.on('mult', (data, cb) => {
    const result = data.numbers[0] * data.numbers[1];
    cb(result);
});

sio.on('client_count', (count) => {
    console.log("we have " + count + " connection(s).")
});

sio.on('room_count', (count) => {
    console.log("we have " + count + " connection(s) in this room.");
});

sio.on('user_joined', (username) => {
    console.log('user ' + username + ' has joined.')
});

sio.on('user_left', (username) => {
    console.log('user ' + username + ' has left.')
});

sio.on('connect_error', (e) => {
    console.log(e.message);
});

sio.on('disconnect', () => {
    console.log("disconnected.");
});



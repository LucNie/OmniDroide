import React, { useEffect } from 'react';
import { NodeJS } from 'nodejs-mobile-react-native';

const App = () => {
  useEffect(() => {
    NodeJS.start('node_scripts/server.js'); // Chargez votre script
    NodeJS.channel.addListener(
      'message',
      (msg) => console.log('Message from NodeJS:', msg),
      this
    );
  }, []);

  return null;
};

export default App;

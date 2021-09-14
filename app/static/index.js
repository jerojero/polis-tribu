// Inspiration: https://github.com/Demos-thinktank/dynata-id/blob/master/site-content/js/index.js

const POLIS_CONVO_ID = '3hmuxjyjzx';
const POLIS_SERVER_URL = 'https://pol.is';

document.addEventListener('readystatechange', event => {
  if (event.target.readyState === 'complete') {
    let xid = getQueryParam('xid');
    // setXid(xid);
    setXid('jero')
  }
});

function getQueryParam (name) {
  const queryParamRe = '[?&]' + encodeURIComponent(name) + '=([^&]*)';
  const queryString = location.search;
  const match = new RegExp(queryParamRe).exec(queryString);
  if (match) {
    return decodeURIComponent(match[1]);
  }
}

function setXid (xid) {
  // Handles the initial handshake between server and iframe
  let messageElem = document.getElementById('message');
  if (typeof xid === 'undefined') {
    messageElem.innerHTML = getMessage('error');
  } else {
    messageElem.innerHTML = getMessage('success');
    attachPolis(xid);
  }
}

function getMessage (type) {
  let message;
  switch (type) {
    case 'error':
      message = "You're missing a designated xid in your URL."
      break;
    case 'success':
      message=null;
      break;
  }
  return message;
}

function attachPolis (xid) {
  let polisContainer = document.getElementById('polis-container');
  let polisHtml = `<div class="polis" data-conversation_id="${POLIS_CONVO_ID}" data-xid="${xid}"></div>`

  let embedScript = document.createElement('script');
  embedScript.src = POLIS_SERVER_URL + '/embed.js';
  embedScript.type = 'text/javascript';
  embedScript.async = true;

  polisContainer.innerHTML = polisHtml;
  polisContainer.appendChild(embedScript);
}

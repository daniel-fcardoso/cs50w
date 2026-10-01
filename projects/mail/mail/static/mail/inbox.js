document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Send email when form is submitted
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function send_email(event) {

  // Prevent the form from reloading the page
  event.preventDefault();

  // Get values from the compose form
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send email to the API
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {

    console.log(result);

    // After sending, open Sent mailbox
    load_mailbox('sent');
  });
}


function load_mailbox(mailbox) {

  // Show mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show mailbox name
  document.querySelector('#emails-view').innerHTML =
    `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get emails from API
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

    emails.forEach(email => {

      // Create div for each email
      const emailDiv = document.createElement('div');

      emailDiv.innerHTML = `
        <strong>${email.sender}</strong>
        <span>${email.subject}</span>
        <span>${email.timestamp}</span>
      `;

      // Basic styling
      emailDiv.style.border = '1px solid #ccc';
      emailDiv.style.padding = '10px';
      emailDiv.style.marginBottom = '5px';

      // Read emails are gray, unread emails are white
      emailDiv.style.backgroundColor = email.read ? '#e9ecef' : 'white';

      // Make email clickable
      emailDiv.style.cursor = 'pointer';

      emailDiv.addEventListener('click', () => {
        view_email(email.id, mailbox);
      });

      // Add email to mailbox
      document.querySelector('#emails-view').append(emailDiv);
    });
  });
}


function view_email(id, mailbox) {

  // Get one email from the API
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {

    // Hide mailbox and compose views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    // Show email view
    document.querySelector('#email-view').style.display = 'block';

    // Display email information
    document.querySelector('#email-view').innerHTML = `
      <div>
        <strong>From:</strong> ${email.sender}
      </div>

      <div>
        <strong>To:</strong> ${email.recipients.join(', ')}
      </div>

      <div>
        <strong>Subject:</strong> ${email.subject}
      </div>

      <div>
        <strong>Timestamp:</strong> ${email.timestamp}
      </div>

      <hr>

      <div>
        ${email.body}
      </div>

      <br>
    `;

    // Mark email as read
    if (!email.read) {
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      });
    }

    // Archive / Unarchive
    if (mailbox !== 'sent') {

      const archiveButton = document.createElement('button');

      archiveButton.className = 'btn btn-sm btn-outline-primary';
      archiveButton.style.marginRight = '5px';

      // Inbox -> Archive
      if (mailbox === 'inbox') {

        archiveButton.innerHTML = 'Archive';

        archiveButton.addEventListener('click', () => {

          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: true
            })
          })
          .then(() => {
            load_mailbox('inbox');
          });
        });
      }

      // Archive -> Unarchive
      else if (mailbox === 'archive') {

        archiveButton.innerHTML = 'Unarchive';

        archiveButton.addEventListener('click', () => {

          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: false
            })
          })
          .then(() => {
            load_mailbox('inbox');
          });
        });
      }

      document.querySelector('#email-view').append(archiveButton);
    }


    // Reply button
    const replyButton = document.createElement('button');

    replyButton.className = 'btn btn-sm btn-outline-primary';
    replyButton.innerHTML = 'Reply';

    replyButton.addEventListener('click', () => {

      // Open compose view
      compose_email();

      // Fill recipient with original sender
      document.querySelector('#compose-recipients').value = email.sender;

      // Add "Re:" only if it is not already there
      if (email.subject.startsWith('Re: ')) {
        document.querySelector('#compose-subject').value = email.subject;
      } else {
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
      }

      // Fill body with original message
      document.querySelector('#compose-body').value =
        `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;

    });

    document.querySelector('#email-view').append(replyButton);

  });
}

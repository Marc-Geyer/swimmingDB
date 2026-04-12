document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');

  // Initial Fetch
  fetch(DATA_URL)
    .then(response => response.json())
    .then(events => {
        calendar.render();
        calendar.addEventSource(events);
    });

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    views:{
      timeGrid:{
        slotMinTime: '8:00',
        scrollTime: '12:00',
        nowIndicator: true,
      }
    },
    businessHours: {
      // days of week. an array of zero-based day of week integers (0=Sunday)
      daysOfWeek: [ 1, 2, 3, 4, 5 ], // Monday - Friday

      startTime: '12:00', // a start time (12pm in this example)
      endTime: '20:00', // an end time (8pm in this example)
    },
    navLinks: true,
    height: 'auto',
    locale: 'de',
    firstDay: 1,

    events: [], // Populated by fetch above

    eventClick: function(info) {
        alert('Session ID: ' + info.event.id + '\nLocation: ' + info.event.extendedProps.location);
    },

    // Styling for cancelled events
    eventClassNames: function(arg) {
        if (arg.event.extendedProps.is_cancelled) {
            return ['bg-gray-300', 'text-gray-500']; // Tailwind classes or custom CSS
        }
        return [];
    }
  });

  calendar.render();

  // WEBSOCKET CONNECTION
  const socket = new WebSocket(WS_URL);

  socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'session_change') {
      const eventSource = calendar.getEventById(data.session_id.toString());

      if (data.action === 'deleted') {
          if (eventSource) eventSource.remove();
      } else {
        if (eventSource) {
          // Update existing
          eventSource.setProp('title', data.payload.title || eventSource.title);
          eventSource.setStart(data.payload.start);
          eventSource.setEnd(data.payload.end);
          eventSource.setExtendedProp('is_cancelled', data.payload.is_cancelled);
          eventSource.setExtendedProp('location', data.payload.location);
          eventSource.setExtendedProp('notes', data.payload.notes);
        } else {
          // Add new (if it wasn't in the initial view range but came in via WS)
          // Note: You might want to check if the date is in the current view before adding
          calendar.addEvent({
              id: data.payload.id,
              title: 'New Session', // Ideally fetch full title from backend or pass in payload
              start: data.payload.start,
              end: data.payload.end,
              extendedProps: data.payload
          });
        }
      }
    }
  };

  socket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
  };
});
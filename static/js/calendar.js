document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    themeSystem: 'bootstrap5',
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

    events: [], // Will be populated by fetch

    // Handle Click
    eventClick: function(info) {
      const props = info.event.extendedProps;
      let msg = `ID: ${info.event.id}\n`;

      if (props.type === 'calculated') {
        msg += `Type: Planned Event (Not yet created)\n`;
        msg += `Plan ID: ${props.plan_id}\n`;
        msg += `Action: Click to create session?`;
      } else {
        msg += `Type: Actual Session\n`;
        msg += `Location: ${props.location || 'N/A'}\n`;
        msg += `Status: ${props.is_cancelled ? 'Cancelled' : 'Active'}\n`;
        if (props.notes) msg += `Notes: ${props.notes}`;
      }

      // In a real app, replace alert with a modal
      if(confirm(msg)) {
        if(props.type === 'calculated') {
           // Trigger creation logic here
           console.log("Creating session for plan:", props.plan_id);
        }
      }
    },

    eventClassNames: function(arg) {
      if (arg.event.extendedProps.is_cancelled) {
        return ['bg-gray-300', 'text-gray-500', 'border-gray-400'];
      }
      return ['bg-blue-500', 'text-white'];
    }
  });

  calendar.render();

   // 1. Initial Fetch
  fetch(DATA_URL)
    .then(response => response.json())
    .then(events => {
      calendar.addEventSource(events);
      console.log("Loaded Events:", events)
      calendar.render();
    })
    .catch(err => console.error("Error loading calendar:", err));

});

export interface Location {
    spot: string;
    city: string;
}
  
export interface Event {
    icon: string;
    type: string;
    title: string;
    time: string;
    location: Location;
    date: string;
}

export interface Day {
    dayNumber: string;
    dateString: string;
    events: Event[];
}

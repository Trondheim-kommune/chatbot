import React from 'react';
/*
This is a simple component that represent a conflict or a search result.
Clicking the button will change the view to a DocumentView
*/
export default class DocumentItem extends React.Component {
  render() {
    return (
      <button
        className="itemButton"
        onClick={() => this.props.changeView('document', this.props.id)}
      >
        {this.props.title} - {this.props.id}
      </button>
    );
  }
}

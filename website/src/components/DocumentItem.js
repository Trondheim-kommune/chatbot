import React from "react"

export default class DocumentItem extends React.Component {
  render() {
    return (
      <p>
        {this.props.title} - {this.props.id}
      </p>
    );

  }
}

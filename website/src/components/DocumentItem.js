import React from "react"

export default class DocumentItem extends React.Component {

  render() {
    return (
      <button onClick={() => this.props.changeView("document", this.props.id)} > {this.props.title} - {this.props.id}</ button>
    );
  }
}

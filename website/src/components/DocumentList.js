import React from "react"
import DocumentItem from "./DocumentItem";

/* 
This component lists multiple DocumentItems
*/
export default class DocumentList extends React.Component {


  render() {
    // Maps through every DocumentItem and display them
    // Each DocumentItem represents a document from the conflict_ids collection
    let documentItems;
    documentItems = this.props.docs.map((doc, i) => (
      <DocumentItem id={doc.id} title={doc.title} key={i} changeView={this.props.changeView} />
    ));
    return (
      <div>
        <h1>{this.props.title}</h1>
        {/* <h1>{this.props.header}</h1> */}
        {documentItems}
      </div>
    );

  }
}

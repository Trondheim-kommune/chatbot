import React, { Component } from "react";
import "./App.css";
import Search from "./components/Search";
import DocumentList from "./components/DocumentList"
import { fetchData } from "./utils/Util";
import DocumentView from "./components/DocumentView";

class App extends Component {
  state = {
    conflictDocs: [],
    searchDocs: [],
    view: "main",
    id: ""
  }

  async componentDidMount() {
    const conflictDocs = await fetchData("http://localhost:8080/v1/get_all_conflict_ids", {});
    this.setState({ conflictDocs });
  }

  changeView = async (view, id) => {
    this.setState({ view, id });
    this.componentDidMount();
  }

  render() {
    return (
      <div>
        {this.state.view === "main" &&
          <div>
            <Search changeView={this.changeView} />
            <DocumentList title="Konflikter" docs={this.state.conflictDocs} changeView={this.changeView} />

          </div>
        }
        {this.state.view === "document" &&
          <DocumentView id={this.state.id} changeView={this.changeView} />
        }
      </div>

    );
  }
}

export default App;

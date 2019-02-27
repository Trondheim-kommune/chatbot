import React, { Component } from "react";
import "./App.css";
import Search from "./components/Search";
import DocumentView from "./components/DocumentList"
import { fetchData } from "./utils/Util";
import ContentView from "./components/DocumentView";

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
  }

  render() {
    return (
      <div>
        <Search />
        {this.state.view === "main" &&
          <DocumentView title="Konflikter" docs={this.state.conflictDocs} changeView={this.changeView} />
        }
        {this.state.view === "document" &&
          <ContentView id={this.state.id} changeView={this.changeView} />
        }
      </div>

    );
  }
}

export default App;

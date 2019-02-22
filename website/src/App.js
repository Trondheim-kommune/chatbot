import React, { Component } from "react";
import "./App.css";
import Search from "./components/Search";
import DocumentView from "./components/DocumentView"
import { fetchData } from "./utils/Util";

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

  // changeView = async (view, id) => {
  //   this.setState({ view, id });
  //   const data = { "data": { "id": id } };
  //   const content = await fetchData("http://localhost:8080/v1/get_content", data);

  //   console.log(content)
  // }

  render() {
    return (
      <div>
        <Search />
        {this.state.view === "main" &&
          <DocumentView title="Konflikter" docs={this.state.conflictDocs} changeView={this.changeView} />
        }
        {this.state.view === "document" &&
          <p>yehaa {this.state.id}</p>
        }
      </div>

    );
  }
}

export default App;

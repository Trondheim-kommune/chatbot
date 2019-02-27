import React from "react"
import { fetchData } from "../utils/Util";
import DocumentList from "./DocumentList"

export default class Search extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      url: '',
      fetched: false
    }
  }
  handleSubmit = async (e) => {
    e.preventDefault();
    // Do something with the url

    const data = { "data": { "url": this.state.url } };
    const content = await fetchData("http://localhost:8080/v1/get_docs_from_url", data);
    if (content.length === 0) {
      alert("Vi fant ingen for den siden, sjekk om URLen stemmer.");
    } else if (content.length > 0) {
      this.setState({ fetched: true, docs: content })
    }
    console.log(content)
  }
  render() {
    return (
      <div>
        <form onSubmit={(e) => this.handleSubmit(e)}>
          <label>
            URL:
            <input type="text"
              value={this.state.url}
              name="url"
              placeholder="https://www.trondheim.kommune.no/"
              onChange={e => this.setState({ url: e.target.value })} />
          </label>
          <input type="submit" value="Search" />
        </form>
        {this.state.fetched &&
          <DocumentList title="Søkeresultater" docs={this.state.docs} changeView={this.props.changeView} />
        }
      </div>
    );

  }
}

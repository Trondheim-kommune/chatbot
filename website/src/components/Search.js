import React from "react"
import { fetchData } from "../utils/Util";
import DocumentList from "./DocumentList"

/* 
This component is a search bar. You search by url and get a DocumentList
containing the search results
*/
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

    // Title and id based on url
    const data = { "data": { "url": this.state.url } };
    const content = await fetchData(process.env.REACT_APP_SERVER_URL + "v1/get_docs_from_url", data);
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
              className="searchInputField"
              value={this.state.url}
              name="url"
              placeholder="https://www.trondheim.kommune.no/"
              onChange={e => this.setState({ url: e.target.value })} />
          </label>
          <input type="submit" value="Search" className="submitSearch" />
        </form>
        {/* If data i fetched, render a DocumentList with the search results */}
        {this.state.fetched &&
          <DocumentList title="Søkeresultater" docs={this.state.docs} changeView={this.props.changeView} />
        }
      </div>
    );

  }
}

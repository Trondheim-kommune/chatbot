import React from 'react';
import { fetchData } from '../utils/Util';
/* 
This component displays the content field in a document from the manual collection
and the corresponding document in the prod collection.
You can edit the "texts" field and the "keywords" field manually.
 */
export default class DocumentView extends React.Component {
  constructor() {
    super();
    this.state = {};
  }

  async componentDidMount() {
    // Fetch content
    const data = { data: { id: this.props.id } };
    const content = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/content/?id=' + this.props.id,
      "GET"
    );
    if (!content.hasOwnProperty('manual')) {
      this.setState({
        manual: content.prod,
        automatic: content.prod,
        url: content.url,
      });
    } else {
      this.setState({
        manual: content.manual,
        automatic: content.prod,
        url: content.url,
      });
    }
  }

  handleSubmit = e => {
    e.preventDefault();
    // Save data and delete entry in manual collection if needed
    const data = { data: { id: this.props.id, content: this.state.manual } };
    const content = fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/content/',
      "POST",
      data
    ).then(() => {
      this.props.changeView('main');
    });
  };

  createNewAnswer = e => {
    e.preventDefault();
    if (this.state.manual) {
      this.setState(prevState => ({
        manual: {
          ...prevState.manual,
          texts: [...prevState.manual.texts, ''],
        },
      }));
    }
  };

  createNewKeyword = e => {
    e.preventDefault();
    if (this.state.manual) {
      this.setState(prevState => ({
        manual: {
          ...prevState.manual,
          keywords: [
            ...prevState.manual.keywords,
            { keyword: '', confidence: 1 },
          ],
        },
      }));
    }
  };

  deleteKeyword = (e, i) => {
    e.preventDefault();
    this.setState(prevState => ({
      manual: {
        ...prevState.manual,
        keywords: [
          ...prevState.manual.keywords.slice(0, i),
          ...prevState.manual.keywords.slice(i + 1),
        ],
      },
    }));
  };

  deleteAnswer = (e, i) => {
    e.preventDefault();
    this.setState(prevState => ({
      manual: {
        ...prevState.manual,
        texts: [
          ...prevState.manual.texts.slice(0, i),
          ...prevState.manual.texts.slice(i + 1),
        ],
      },
    }));
  };

  deleteDocument = (e, i) => {
    e.preventDefault();
    const document = { data: { id: this.props.id } };
    fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/doc',
      'DELETE',
      document
    ).then(() => {
      this.props.changeView('main');
    });
  }

  render() {
    let textAreasManual;
    if (this.state.manual) {
      /* map through the texts field from manual */
      textAreasManual = this.state.manual.texts.map((text, i) => (
        <div key={i} className="answers">
          <div className="answer">
            <textarea
              rows="10"
              cols="50"
              value={text}
              onChange={e => {
                const value = e.target.value;

                this.setState(prevState => ({
                  manual: {
                    ...prevState.manual,
                    texts: [
                      ...prevState.manual.texts.slice(0, i),
                      value,
                      ...prevState.manual.texts.slice(i + 1),
                    ],
                  },
                }));
              }}
            />
          </div>
          <button type="button" className="deleteText" onClick={e => this.deleteAnswer(e, i)}>
            Slett svar
          </button>
        </div>
      ));
    }

    let keywordsManual;
    if (this.state.manual) {
      /* Map through the keywords from manual */
      keywordsManual = this.state.manual.keywords.map((keyword, i) => (
        <div key={i} className="keyword" className="keywordManual">
          <input
            type="text"
            value={keyword['keyword']}
            className="keywordWord"
            onChange={e => {
              e.preventDefault();
              const value = e.target.value;
              this.setState(prevState => ({
                manual: {
                  ...prevState.manual,
                  keywords: [
                    ...prevState.manual.keywords.slice(0, i),
                    {
                      keyword: value,
                      confidence: prevState.manual.keywords[i].confidence,
                    },
                    ...prevState.manual.keywords.slice(i + 1),
                  ],
                },
              }));
            }}
          />
          <input
            className="confidence"
            type="number"
            min="0"
            max="1"
            step="0.000000000000000001"
            value={keyword['confidence']}
            onChange={e => {
              e.preventDefault();
              const value = parseFloat(e.target.value);
              this.setState(prevState => ({
                manual: {
                  ...prevState.manual,
                  keywords: [
                    ...prevState.manual.keywords.slice(0, i),
                    {
                      keyword: prevState.manual.keywords[i].keyword,
                      confidence: value,
                    },
                    ...prevState.manual.keywords.slice(i + 1),
                  ],
                },
              }));
            }}
          />
          <button
            className="deleteKeyword"
            type="button"
            onClick={e => this.deleteKeyword(e, i)}
          >
            Slett nøkkelord
          </button>
        </div>
      ));
    }

    let textAreasAutomatic;
    if (this.state.automatic) {
      /* Map through the texts field from prod */
      textAreasAutomatic = this.state.automatic.texts.map((text, i) => (
        <textarea readOnly key={i} rows="10" cols="50" value={text} />
      ));
    }

    let keywordsAutomatic;
    if (this.state.automatic) {
      /* Map through the keywords field from prod */
      keywordsAutomatic = this.state.automatic.keywords.map((keyword, i) => (
        <div key={i} className="keyword">
          <input readOnly type="text" value={keyword['keyword']} />
          <input readOnly type="text" value={keyword['confidence']} />
        </div>
      ));
    }

    return (
      <div>
        <button onClick={e => this.props.changeView('main')}>Tilbake</button>
        {this.state.url && (
          <h1 className="title">
            <a href={this.state.url}>{this.state.url}</a>
          </h1>
        )}
        <div className="flex">
          {this.state.manual && (
            <div className="sub-container">
              <h2>Manuelle endringer</h2>
              <p>
                Her kan du endre svarene til botten manuelt. Oppdater teksten og
                trykk på lagre for å oppdatere.
            </p>
              <form>
                <strong>Svar:</strong>
                {textAreasManual}
                <button
                  className="newText"
                  type="button"
                  onClick={e => this.createNewAnswer(e)}
                >
                  Nytt svar
              </button>
                <p>
                  Man kan også oppdatere, legge til og slette nøkkelord og
                  selvsikkerheten deres.
              </p>
                <p>
                  Selvsikkerheten er et tall fra 0 til 1. 1 om du må ha dette
                  søketordet for å få dette svaret.
              </p>
                <p>
                  <strong>Nøkkelord:</strong>
                </p>
                {keywordsManual}
                <button
                  className="newKeyword"
                  type="button"
                  onClick={e => this.createNewKeyword(e)}
                >
                  Nytt nøkkelord
              </button>
                <input type="button" value="Lagre" className="save" onClick={e => this.handleSubmit(e)} />
                <input type="button" value="Slett" className="delete" onClick={e => this.deleteDocument(e)} />
              </form>
            </div>
          )}
          {this.state.automatic && (
            <div className="sub-container">
              {this.state.url && (
                <h2>
                  {' '}
                  Automatisk hentet fra{' '}
                  <a href={this.state.url}>{this.state.url}</a>
                </h2>
              )}
              <p>
                Sammenlign de manuelle endringene med informasjonen hentet fra
                nettsiden
            </p>
              <p>
                <strong>Svar:</strong>
              </p>
              {textAreasAutomatic}
              <p>
                <strong>Nøkkelord:</strong>
              </p>
              {keywordsAutomatic}
            </div>
          )}
        </div>
      </div>
    );
  }
}

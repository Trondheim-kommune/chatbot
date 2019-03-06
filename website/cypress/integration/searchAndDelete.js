// A two second wait time to make sure everything is loaded
const waitTime = 2000;


// This test will search for a site, select the first document, and
// delete the last entries
describe('Test search and deleting text and keyword', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/')
      .wait(waitTime);
  });

  it('Search and delete answere and keyword for the first result ', () => {
    const url = 'https://www.trondheim.kommune.no'
    // Type the url in the search bar
    cy.get('.searchInputField')
      .type(url)
      .should('have.value', url)
      .wait(waitTime);

    // Click the search button
    cy.get('.submitSearch').first()
      .click()
      .wait(waitTime);

    const title = ' Velkommen til Trondheim kommune - 295cc564fe771fbb92b3278a6eee2d5cbcae2606-3'
    // Get the first result after searching and check text is what we expect
    cy.get('.itemList').first().children('.itemButton').first()
      .invoke('text').then((text => {
        expect(text).to.eq(title)
      }));

    // click the first result
    cy.get('.itemList').first().children('.itemButton').first()
      .click()
      .wait(waitTime);

    // Delete last text entry
    cy.get('.answers').children().last()
      .click();

    // Delete last keyword entry
    cy.get('.keywordManual').last().children('.deleteKeyword')
      .click()

    // Click the save button
    cy.get('.save')
      .click()
  });
}); 
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { MensagemService } from 'core/mensagem/mensagem.service';

// Apollo
import { Apollo, ApolloModule } from 'apollo-angular';
import { HttpLink, HttpLinkHandler } from 'apollo-angular/http';
import { ApolloLink, from, InMemoryCache } from '@apollo/client/core';
import { ErrorResponse, onError } from '@apollo/client/link/error';
import { environment } from 'environments/environment';

const uri = '';
// const uri = environment.api_graphql;
const graphqlUriSufix = '/';

@NgModule({
    imports: [HttpClientModule, ApolloModule],
    exports: [HttpClientModule],
})
export class GraphQLModule {
    constructor(apollo: Apollo, httpLink: HttpLink, mensagem: MensagemService) {
        const errorLink = onError(
            ({
                graphQLErrors,
                networkError,
                operation,
                forward,
            }: ErrorResponse) => {
                if (graphQLErrors) {
                    graphQLErrors.map(
                        ({ message, locations, path, extensions }) => {
                            console.error(
                                '[GraphQL error]: ' +
                                    message +
                                    ' - ' +
                                    locations +
                                    ' - ' +
                                    path +
                                    ' - ' +
                                    extensions
                            );
                            mensagem.erro(extensions['errorMessage']);
                        }
                    );
                }

                if (networkError) {
                    switch (networkError['status']) {
                        case 401:
                            mensagem.erro('Você não está logado');
                            // window.location.href = environment.url_base;
                            break;
                        case 500:
                            mensagem.erro('Erro interno no servidor!');
                            break;
                        case 504:
                            mensagem.erro('Serviço indisponível!');
                            break;
                        case 404:
                            mensagem.erro('Recurso não encontrado!');
                            break;
                        default:
                            alert('Erro de Conexão! Tempo Excedido.');
                            break;
                    }
                }

                return forward(operation);
            }
        );

        const loggerLink = new ApolloLink((operation, forward) => {
            operation.setContext({ start: new Date() });
            return forward(operation).map((response) => {
                const responseTime = new Date().getMilliseconds();
                -operation.getContext().start.getMilliseconds();
                return response;
            });
        });

        // create Apollo link para a api do simp (default)
        this.criarApolloLink(
            apollo,
            errorLink,
            loggerLink,
            this.obterHttpLinkHandler(httpLink)
        );
    }

    private obterHttpLinkHandler(httpLink: HttpLink) {
        let uriEndpoint = uri + graphqlUriSufix;
        return httpLink.create({
            uri: uriEndpoint,
            withCredentials: true, // is simply passed to the HttpClient used by the HttpLink when sending the query.
            includeExtensions: true,
        });
    }

    private criarApolloLink(
        apollo: Apollo,
        errorLink,
        loggerLink,
        httpLinkHandler: HttpLinkHandler,
        name?: string
    ) {
        apollo.create(
            {
                link: from([errorLink, loggerLink, httpLinkHandler]),
                cache: new InMemoryCache({
                    addTypename: false,
                }),
                defaultOptions: {
                    watchQuery: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                    query: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                    mutate: {
                        errorPolicy: 'all',
                    },
                },
            },
            name ? name : null
        );
    }
}

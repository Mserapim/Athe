/**
 *
 **/
Ext._define('rh.publicacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.publicacao.Window',

    keywordFieldMessage: 'Texto',

    remoteColumnModel: true,

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'publication', '-', 'search', '->'],

    rendererBoolean: function(value){
        return '<div style="text-align:center">' + (value ? 'SIM' : 'NÃO') + '</div>';
    },

    sentToPublication: function() {
        var selected = this.getSelectionModel().getSelections();

        if(selected.length === 1) {
            var wnd = Ext._create('rh.publicacao.SentToPublicationWindow', {
                values: selected[0].data,
                oId: selected[0].get('pk'),
                grid: this
            });

            wnd.show();
        }
    },

    confirmPublication: function() {
        var selected = this.getSelectionModel().getSelections();

        if(selected.length === 1) {
            var wnd = Ext._create('rh.publicacao.ConfirmPublicationWindow', {
                values: selected[0].data,
                oId: selected[0].get('pk'),
                grid: this
            });

            wnd.show();
        }
    },

    getPublicationAction: function() {
        if(!this._publicationAction)
            this._publicationAction = Ext._create('Ext.Button', {
                text: 'Publicar',
                hideLabel: false,
                menu: [
                    {
                        text: 'Enviar ao veículo de publicação',
                        keyId: 'm1',
                        scope: this,
                        handler: function() { this.sentToPublication(); }
                    },
                    {
                        text: 'Confirmar publicação',
                        keyId: 'm2',
                        scope: this,
                        handler: function() { this.confirmPublication(); }
                    },
                    '-',
                    {
                        text: 'Cancelar publicação',
                        keyId: 'm3',
                        scope: this,
                        handler: function() {
                        }
                    }
                ]
            });

        return this._publicationAction;
    },

    filterByPublicationState: function(state) {
        this._filterByPublicationState = core.nullValue(
            this._filterByPublicationState,
            [1, 2, 3, 4]
        );

        if(this._filterByPublicationState.indexOf(state) >= 0)
            this._filterByPublicationState.remove(state);
        else
            this._filterByPublicationState.push(state);

        this.setFilterProperty('publication_state__in', this._filterByPublicationState, 10);
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Mostrar publicação em aberto',
                    checked: true,
                    hideOnClick: false,
                    scope: this,
                    checkHandler: function() { this.filterByPublicationState(1); }
                },
                {
                    text: 'Mostrar publicação solicitada',
                    checked: true,
                    hideOnClick: false,
                    scope: this,
                    checkHandler: function() { this.filterByPublicationState(2); }
                },
                {
                    text: 'Mostrar publicação confirmada',
                    checked: true,
                    hideOnClick: false,
                    scope: this,
                    checkHandler: function() { this.filterByPublicationState(3); }
                },
                {
                    text: 'Mostrar publicação cancelada',
                    checked: true,
                    hideOnClick: false,
                    scope: this,
                    checkHandler: function() { this.filterByPublicationState(4); }
                }
            ];

        return this._filterMenu;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid},
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Nome', dataIndex: 'cache_unicode', width: 100, id: 'autoExpandColumn'},
                    {header: 'Tipo', dataIndex: 'tipo_display', width: 100, hidden: true},
                    {header: 'Número', dataIndex: 'numero', width: 80, hidden: true},
                    {header: 'Data expedição', dataIndex: 'data_expedicao', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true},
                    {header: 'Data vigência', dataIndex: 'data_vigencia', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true},
                    {header: 'Data publicação', dataIndex: 'data_publicacao', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true},
                    {header: 'Origem', dataIndex: 'origem_unicode', minWidth: 100, hidden: true},
                    {header: 'Publicado', dataIndex: 'veiculo_publicacao_display', width: 240, hidden: true},
                    {header: 'Interno', dataIndex: 'interno', width: 80, renderer: this.rendererBoolean},
                    {header: 'Interessado', dataIndex: 'interessado_nome', width: 200, hidden: true}
                ]
            );

        return this._columnModel;
    },

    _publishState: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this.__publishState = value;

            if(dispatch)
                this._observePublishState();
        }

        return this.__publishState;
    },

    _observePublishState: function() {
        value = this._publishState();

        if(value && value == 1) {
            this.getPublicationAction().enable();
            this.getPublicationAction().menu.items.each(
                function(item) {
                    if(item.keyId === 'm2')
                        item.disable();
                    else
                        item.enable();
                }
            );
        }
        else if(value && value == 2) {
            this.getPublicationAction().enable();
            this.getPublicationAction().menu.items.each(
                function(item) {
                    if(item.keyId === 'm1')
                        item.disable();
                    else
                        item.enable();
                }
            );
        }
        else
            this.getPublicationAction().disable();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.publicacao.Grid.superclass.constructor.call(this, cfg);

        this.getSelectionModel().on({
            scope: this,
            selectionchange: function(sel) {
                var selected = sel.getSelections();

                if(selected.length == 1)
                    this._publishState(selected[0].get('publication_state'));
                else
                    this._publishState(null);
            }
        });

        this._observePublishState();
    }
});

core.RestfulGrid.register(
    'rh.publicacao.Restful',
    'rh.publicacao.Grid'
);

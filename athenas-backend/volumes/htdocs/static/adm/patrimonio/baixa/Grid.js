/**
 *
 **/
Ext._define('adm.patrimonio.baixa.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.baixa.Window',

    mixins: {
        0: 'adm.patrimonio.entrada.Grid'
    },

    statics: {
        types: [],

        register: function(name, label, iconCls, Class) {
            adm.patrimonio.baixa.Grid.types.push({
                name: name,
                label: label,
                iconCls: iconCls,
                Class: Class
            });
        },

        getClassByName: function(name) {
            var Class = false;

            adm.patrimonio.baixa.Grid.types.forEach(
                function(item) {
                    if(item.name == name) {
                        Class = item.Class;
                        return false;
                    }
                }
            );

            return Class;
        },

        getNewMenu: function(scope) {
            if(adm.patrimonio.baixa.Grid.types.length > 0) {
                return adm.patrimonio.baixa.Grid.types.map(
                    function(item) {
                        return {
                            text: item.label,
                            scope: scope,
                            iconCls: item.iconCls,
                            handler: function() {
                                this.createItem(item.Class);
                            }
                        };
                    }
                );
            }
            else
                return [
                    {
                        text: 'Nenhum tipo foi especificado',
                        enable: false
                    }
                ];
        }
    },

    toogleFilterState: function(state) {
        var filterState = core.nullValue(this._fitlerState, [1, 2]);

        if(filterState.indexOf(state) >= 0)
            filterState.remove(state);
        else
            filterState.push(state);

        this._fitlerState = filterState;
        this.setFilterProperty('state__in', this._fitlerState, 1000);
    },

    getFilterMenu: function() {

        return [
            {
                text: 'Notas em Aberto',
                checked: true,
                hideOnClick: false,
                scope: this,
                handler: function() { this.toogleFilterState(1); }
            },
            {
                text: 'Notas Fechadas',
                checked: true,
                hideOnClick: false,
                scope: this,
                handler: function() { this.toogleFilterState(2); }
            },
            {
                text: 'Notas Canceladas',
                checked: false,
                hideOnClick: false,
                scope: this,
                handler: function() { this.toogleFilterState(3); }
            }
        ];
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 70, menuDisabled: true, renderer: adm.daily.rendererIconGrid},
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Conta', dataIndex: 'conta_unicode', width: 160},
                    {header: 'Numero', dataIndex: 'cache_numero', width: 95},
                    {header: 'Processo', dataIndex: 'processo', width: 95},
                    {header: 'Preparação', dataIndex: 'pre_baixa_unicode', width: 135},
                    {header: 'Documento', dataIndex: 'documento', width: 145},
                    {header: 'Data do Doc.', dataIndex: 'data_documento', width: 95, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Data da Baixa.', dataIndex: 'data_baixa', width: 95, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                ]
            );

        return this._columnModel;
    },

    createItem: function(classDef) {
        var values = {};
        var ClassBase;

        if(classDef.type) {
            ClassBase = adm.patrimonio.baixa.Grid.getClassByName(classDef.type);
            values = classDef;
        }
        else {
            ClassBase = classDef;
        }

        Ext._create(
            ClassBase,
            {
                action: 'create',
                params: this.getParams(),
                values: {},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }
        ).show();
    },

    updateItem: function(record) {
        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            var Class = adm.patrimonio.baixa.Grid.getClassByName(selected.get('type'));
            Ext._create(Class, {
                action: 'update',
                oId: selected.get('pk'),
                values: 'remote',
                params: this.getParams(),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    changeState: function(state) {
        var selection = this.getSelectionModel().getSelections();
        var cfg = false;
        var rest = this.factoryRestful();

        if(selection.length == 1) {
            cfg = {
                params: {
                    state: state
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            };

            rest.update(
                selection[0].get('pk'),
                cfg,
                {
                    el: this.getEl(),
                    message: 'Atualizando o estado da nota de baixa.'
                }
            );
        }
        else if(selection.length > 1) {
            cfg = {
                params: {
                    state: state,
                    filter: Ext.encode([
                        {
                            property: 'pk__in',
                            value: selection.map(
                                function(s) { return s.get('pk'); }
                            )
                        }
                    ])
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            };

            rest.update(
                false,
                cfg,
                {
                    el: this.getEl(),
                    message: 'Atualizando o estado da nota de baixa.'
                }
            );
        }
        else {
            Ext.Msg.show({
                title: 'Nota de baixa',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione os itens que deseja mudar o estado.'
            });
        }
    },

    reportLowTerm: function() {
        var selection = this.getSelectionModel().getSelected();
        if (selection){

            engine.mq.Report.request({
                report: '/to/mpe/adm/patrimonio/termo_de_baixa',

                el: this.getEl(),

                waitMessage: 'Gerando relatório...',

                params: {

                    outfile: 'termo_de_baixa-' + selection.get('processo'),

                    report_name: 'Termo de Baixa - ' + selection.get('processo'),

                    baixa: selection.get('pk'),

                }

            });

        } else {

            Ext.Msg.show({

                title: 'Atenção',

                icon: Ext.Msg.INFO,

                buttons: Ext.Msg.OK,

                msg: 'Selecione pelo menos um item.'

            });
        }
    },

    getToolbar: function(cfg) {
        var novoComponent;

        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.baixa.Grid.superclass.getToolbar.call(this, cfg);

            this._toolbar.findBy(
                function(item) {
                    if(item.text == 'Novo')
                        novoComponent = item;
                }
            );

            this._toolbar.remove(novoComponent);
            this._toolbar.insert(0, {
                text: 'Nova baixa',
                iconCls: 'icon-core icon-core-add',
                menu: adm.patrimonio.baixa.Grid.getNewMenu(this)
            });

            this._toolbar.insert(
                3,
                {
                    text: 'Relatórios',
                    iconCls: 'icon-core icon-core-reports',
                    menu: [
                        {
                            text: 'Termo de Baixa',
                            iconCls: 'icon-patrimonio icon-pat-nota-aberta',
                            scope: this,
                            handler: this.reportLowTerm
                        }
                    ]
                }
            );

            this._toolbar.insert(
                3, '-'
            );

            this._toolbar.insert(
                3,
                {
                    text: 'Status',
                    iconCls: 'icon-patrimonio icon-pat-nota',
                    menu: [
                        {
                            text: 'Nota Aberta',
                            iconCls: 'icon-patrimonio icon-pat-nota-aberta',
                            scope: this,
                            handler: function() { this.changeState(1); }
                        },
                        {
                            text: 'Nota Fechada',
                            iconCls: 'icon-patrimonio icon-pat-nota-finalizada',
                            scope: this,
                            handler: function() { this.changeState(2); }
                        },
                        {
                            text: 'Nota Cancelada',
                            iconCls: 'icon-patrimonio icon-pat-nota-cancelada',
                            scope: this,
                            handler: function() { this.changeState(3); }
                        }
                    ]
                }
            );

            this._toolbar.insert(
                3, '-'
            );
        }

        return this._toolbar;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.baixa.Restful',
    'adm.patrimonio.baixa.Grid'
);

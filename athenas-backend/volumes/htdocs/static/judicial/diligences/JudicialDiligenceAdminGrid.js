
Ext._define('judicial.diligences.JudicialDiligenceAdminGrid', {
    extend: 'judicial.diligences.JudicialDiligenceGrid',

    configOrderToolBar: ['search', 'actions', '-', 'giveBack', '-', 'openPrinter', '-', '->'],

    officerGrid: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._officerGrid = value;
        }

        return this._officerGrid;
    },

    getReportSelectedDiligencesAction: function(cfg) {
        if(!this._reportSelectedDiligences)
            this._reportSelectedDiligences = Ext._create('Ext.Button', {
                text: 'Gerar documento de diligência',
                scope: this,
                handler: function() { this.reportSelectedDiligences(); }
            });

        return this._reportSelectedDiligences;
    },

    cleanFilter: function(noLoad) {
        this._filterStatus = [2, 3, 4, 5];
        noLoad = core.nullValue(noLoad, false);

        this.setFilterProperty('delivery_status__in', this._filterStatus, 1000, !noLoad);
    },

    filterOficialDiligencia: function() {
        Ext._create(
            'judicial.diligences.FilterOfficcerDiligenceWindow',
            { grid: this }
        ).show();
    },

    filterCounty: function () {
        Ext._create(
            'judicial.diligences.FilterCountyWindow',
            { grid: this }
        ).show();
    },

    filterOrigin: function() {
        Ext._create(
            'judicial.diligences.FilterOriginWindow',
            { grid: this }
        ).show();
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    'text': 'Por Comarca',
                    'scope':this,
                    'handler': this.filterCounty
                },
                '-',
                {
                    'text': 'Por Oficial de Diligência',
                    'scope': this,
                    'handler': this.filterOficialDiligencia
                },
                '-',
                {
                    'text': 'Por Origem',
                    'scope':this,
                    'handler':this.filterOrigin
                }
            ];

        return this._filterMenu;
    },

    getActionsAction: function(cfg) {
        if(!this._actionActions)
            this._actionActions = Ext._create('Ext.Button', {
                text: 'Ações',
                iconCls: 'icon-core icon-core-run',
                menu: [
                    {
                        text: 'Retirar Oficial da Diligência',
                        iconCls: 'icon-judicial icon-ejud-clean-definition',
                        scope: this,
                        handler: this._removeFromOfficer
                    },
                    {
                        text: 'Delegar Oficial Aleatóriamente',
                        iconCls: 'icon-judicial icon-ejud-confirm-diligence',
                        scope: this,
                        handler: this._sendToRandomOfficer
                    },
                    {
                        'text': 'Delegar Oficial Manualmente',
                        'scope': this,
                        'handler': this._sendToOfficer,
                        'iconCls': 'icon-judicial icon-ejud-confirm-diligence'
                    },
                ]
            });

        return this._actionActions;
    },

    getGiveBackAction: function() {
        if (!this._giveBackAction) {
            this._giveBackAction = Ext._create('Ext.Button', {
                text: 'Devolver',
                iconCls: 'icon-judicial icon-ejud-give-back-diligence',
                scope: this,
                handler: function() { this.openGiveBackWindow() }
            });
        }

        return this._giveBackAction;
    },

    openGiveBackWindow: function(selection) {
        var selections = this.getSelectionModel().getSelections();

        if (selections.length == 1) {
            Ext._create('judicial.diligences.GiveBackWindow', {
                action: 'create',
                params: {
                    diligence: selections[0].get('pk')
                },
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
        else if (selections.length > 1)
            Ext.Msg.show({
                'title': 'Erro',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Só é possível devolver uma Diligência por vez.'
            });
        else
            Ext.Msg.show({
                'title': 'Erro',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione uma Diligência para executar essa ação.'
            });
    },

    _sendToRandomOfficer: function() {
        var diligences;

        diligences = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });

        if(diligences.length < 1) {
            Ext.Msg.show({
                title: 'Informando oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia para ser entregue ao oficial.'
            });

            return;
        }

        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Informando oficial de diligencia...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('send_to_random_officer_diligence', false, 'POST', {
                scope: this,
                params: {
                    pkset: diligences
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.getStore().reload();
                        if(this.officerGrid())
                            this.officerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Informando oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Informando oficial',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

    _sendToOfficer: function() {
        var officer, diligences;

        if(!this.officerGrid())
            throw 'Não foi definido o grid de oficiais, desta forma não é possivel continuar';

        officer = this.officerGrid().getSelectionModel().getSelected();
        if(!officer) {
            Ext.Msg.show({
                title: 'Informando oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primerio selecione um oficial de diligência para poder marcar as diligências.'
            });

            return;
        }
        else
            officer = officer.get('pk');

        diligences = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });

        if(diligences.length < 1) {
            Ext.Msg.show({
                title: 'Informando oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia para ser entregue ao oficial.'
            });

            return;
        }

        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Informando oficial de diligencia...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('send_to_officer_diligence', false, 'POST', {
                scope: this,
                params: {
                    pkset: diligences,
                    officer: officer
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.getStore().reload();
                        if(this.officerGrid())
                            this.officerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Informando oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Informando oficial',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

    _removeFromOfficer: function() {
        var diligences;

        diligences = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });

        if(diligences.length < 1) {
            Ext.Msg.show({
                title: 'Removendo oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia.'
            });

            return;
        }

        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desassociado oficial de diligencia...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('remove_from_officer_diligence', false, 'POST', {
                scope: this,
                params: {
                    pkset: diligences
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.getStore().reload();
                        if(this.officerGrid())
                            this.officerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Removendo oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Removendo oficial',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },
});

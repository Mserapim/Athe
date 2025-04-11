/**
 *
 **/
Ext._define('judicial.diligences.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getWaitingDiligencesGrid: function() {
        if (!this._waitingDiligencesGrid) {
            this._waitingDiligencesGrid = Ext._create('judicial.diligences.JudicialDiligenceAdminGrid', {
                region: 'center',
                minWidth: 400,
                width: 700,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
            });

            this._waitingDiligencesGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (sm) {
                    var selection = sm.getSelections();

                    if (selection.length > 0)
                        this.diligences(selection[0].get('pk'));
                    else
                        this.diligences(null);
                }
            });

            this._waitingDiligencesGrid.officerGrid(this.getOfficerGrid());
            this._waitingDiligencesGrid.setFilterProperty('delivery_status__in', [2, 3], 1000);

            this._waitingDiligencesGrid.addEvents('afterGiveBackDiligence');

            this._waitingDiligencesGrid.on({
                scope: this,
                afterGiveBackDiligence: function() {
                    this._waitingDiligencesGrid.getStore().reload();
                }
            });
        }

        return this._waitingDiligencesGrid;
    },

    getDeliveryDiligencesGrid: function() {
        if (!this._deliveryDiligencesGrid) {
            this._deliveryDiligencesGrid = Ext._create('judicial.diligences.JudicialDiligenceAdminGrid', {
                region: 'center',
                minWidth: 400,
                width: 700,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                configOrderToolBar: ['search', 'openPrinter', '->'],
            });

            this._deliveryDiligencesGrid.setFilterProperty('delivery_status__in', [4], 1000);
        }

        return this._deliveryDiligencesGrid;
    },

    getReturnedDiligencesGrid: function () {
        if (!this._returnedDiligencesGrid) {
            this._returnedDiligencesGrid = Ext._create('judicial.diligences.JudicialDiligenceAdminGrid', {
                region: 'center',
                minWidth: 400,
                width: 700,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                configOrderToolBar: ['search', 'openPrinter', '->'],
            });

            this._returnedDiligencesGrid.setFilterProperty('delivery_status__in', [8], 1000);
        }

        return this._returnedDiligencesGrid;
    },

    getAnswerDiligencesGrid: function() {
        if (!this._answerDiligencesGrid) {
            this._answerDiligencesGrid = Ext._create('judicial.diligences.JudicialDiligenceAdminGrid', {
                region: 'center',
                minWidth: 400,
                width: 700,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                configOrderToolBar: ['search', 'openPrinter', '->'],
            });

            this._answerDiligencesGrid.setFilterProperty('delivery_status__in', [5, 9, 10, 11, 99], 1000);
        }

        return this._answerDiligencesGrid;
    },

    getOfficerGrid: function() {
        if (!this._officerGrid) {
            this._officerGrid = Ext._create('judicial.diligences.officer.DiligenceGrid', {
                title: 'Oficiais de Diligências',
                region: 'east',
                minWidth: 350,
                width: 350,
                split: true,
                allowAdd: false,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                enabled: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                gridAutoLoad: false
            });

            this._officerGrid.setFilterProperty('status', 1, 100);
        }

        return this._officerGrid;
    },

    diligences: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._diligences = value;

            if (!prevent)
                this.observeDiligences();
        }

        return this._diligences;
    },

    observeDiligences: function() {
        value = this.diligences();
        if (value) {
            this.getOfficerGrid().enable();
        }
        else {
            this.getOfficerGrid().disable();
        }
    },

    _sendToRandomOfficer: function() {
        var diligences;

        diligences = this.getWaitingDiligencesGrid().getSelectionModel().getSelections().map(function (data) {
            return data.get('pk');
        });

        if (diligences.length < 1) {
            Ext.Msg.show({
                title: 'Informando oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia para ser entregue ao oficial.'
            });

            return;
        }

        var rest = this.getWaitingDiligencesGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Informando oficial de diligencia...' });

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
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        this.getWaitingDiligencesGrid().getStore().reload();
                        this.getOfficerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Informando oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function (xhr) {
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

        officer = this.getOfficerGrid().getSelectionModel().getSelected();
        if (!officer) {
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

        diligences = this.getWaitingDiligencesGrid().getSelectionModel().getSelections().map(function (data) {
            return data.get('pk');
        });

        if (diligences.length < 1) {
            Ext.Msg.show({
                title: 'Informando oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia para ser entregue ao oficial.'
            });

            return;
        }

        var rest = this.getWaitingDiligencesGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Informando oficial de diligencia...' });

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
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        this.getWaitingDiligencesGrid().getStore().reload();
                        this.getOfficerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Informando oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function (xhr) {
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

        diligences = this.getWaitingDiligencesGrid().getSelectionModel().getSelections().map(function (data) {
            return data.get('pk');
        });

        if (diligences.length < 1) {
            Ext.Msg.show({
                title: 'Removendo oficial',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione pelo menos uma diligencia.'
            });

            return;
        }

        var rest = this.getWaitingDiligencesGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Desassociado oficial de diligencia...' });

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
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        this.getWaitingDiligencesGrid().getStore().reload();
                        this.getOfficerGrid().getStore().reload();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Removendo oficial',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function (xhr) {
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

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Diligências',
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    {
                        xtype: 'tabpanel',
                        region: 'center',
                        activeTab: 0,
                        border: false,
                        items: [
                            {
                                xtype: 'container',
                                title: 'Aguardando Distribuição/Oficial',
                                region: 'center',
                                layout: 'border',
                                items: [
                                    this.getWaitingDiligencesGrid(),
                                    this.getOfficerGrid()
                                ]
                            },
                            {
                                xtype: 'container',
                                title: 'Em Entrega',
                                region: 'center',
                                layout: 'border',
                                items: [
                                    this.getDeliveryDiligencesGrid(),
                                ]
                            },
                            {
                                xtype: 'container',
                                title: 'Devolvidas',
                                region: 'center',
                                layout: 'border',
                                items: [
                                    this.getReturnedDiligencesGrid(),
                                ]
                            },
                            {
                                xtype: 'container',
                                title: 'Finalizadas',
                                region: 'center',
                                layout: 'border',
                                items: [
                                    this.getAnswerDiligencesGrid(),
                                ]
                            }
                        ]
                    },
                ]
            }
        );

        judicial.diligences.Manage.superclass.constructor.call(this, cfg);
    }
});

Ext._define('corregedoria.inspection.inspection.SendCommunicationCPJCSMP', {
    extend: 'Ext.Window',

    getDateStartField: function() {
        if(!this._dateStartField) {
            this._dateStartField = new Ext.form.DateField({
                emptyText: 'Início',
                format: 'd/m/Y',
                width: 90,
                enableKeyEvents: true,
            });
        }
        return this._dateStartField;
    },

    getDateEndField: function() {
        if(!this._dateEndField) {
            this._dateEndField = new Ext.form.DateField({
                emptyText: 'Fim',
                format: 'd/m/Y',
                width: 90,
                enableKeyEvents: true,
            });
        }
        return this._dateEndField;
    },

    getGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.inspection.inspection.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 710,
                gridAutoLoad: true,
                columnAction: false,
                hideColumns: ['icons', 'operability_score', 'promptness_score', 'final_score'],
                configOrderToolBar: [],
                doubleClickHandler: function() {},
            });
            this._grid.addFilterProperty('signs', null, -1, false);
            this._grid.addFilterProperty('communicated_cpjcsmp', true, -2, true);
            // this._grid.addFilterProperty('communicated_organ_execution', true, 3, false);
        }
        this._grid._toolbar.insert(1,'Período da Inspeção/Correição:');
        this._grid._toolbar.insert(2,this.getDateStartField());
        this._grid._toolbar.insert(3,'-');
        this._grid._toolbar.insert(4,this.getDateEndField());
        this._grid._toolbar.insert(5,'-');
        this._grid._toolbar.insert(6,
            {
                xtype: 'button',
                text: 'Filtrar',
                iconCls: true,
                icon: '/' + global.Context + '/static/images/find.png',
                scope: this,
                handler: function() {
                    this.setFilterParams(cfg);
                },
            }
        );
        this._grid._toolbar.insert(7,
            {
                xtype: 'button',
                text: 'Limpar',
                iconCls: true,
                icon: '/' + global.Context + '/static/images/clear-all.png',
                scope: this,
                handler: function() {
                    this.clearrParams(cfg);
                }
            }
        );
        this._grid._toolbar.insert(8,'->');
        this._grid._toolbar.insert(9,'-');
        return this._grid;
    },

    setFilterParams: function(cfg){
        var dateStart = this.getDateStartField().getValue() ? Ext.util.Format.date(this.getDateStartField().getValue(), 'Y-m-d') : '';
        var dateEnd = this.getDateEndField().getValue() ? Ext.util.Format.date(this.getDateEndField().getValue(), 'Y-m-d') : '';
        var params = [];
        params.push({'property': 'signs', 'value': null, 'stage': -1});
        params.push({'property': 'communicated_cpjcsmp', 'value': true, 'stage': -2});
        // params.push({'property': 'communicated_organ_execution', 'value': true, 'stage': 3});
        if(dateStart !== '' && dateEnd === ''){
            params.push({'property': 'inspection_date_initial__gte', 'value': dateStart, 'stage': 4});
        }else if(dateEnd !== '' && dateStart === ''){
            params.push({'property': 'inspection_date_final__lte', 'value': dateEnd, 'stage': 4});
        }else if(dateStart !== '' && dateEnd !== ''){
            params.push({'property': 'inspection_date_initial__gte', 'value': dateStart, 'stage': 4});
            params.push({'property': 'inspection_date_final__lte', 'value': dateEnd, 'stage': 5});
        }
        this.getGrid(cfg).setFilter(params);
    },

    clearrParams: function(cfg){
        var params = [];
        params.push({'property': 'signs', 'value': null, 'stage': -1});
        params.push({'property': 'communicated_cpjcsmp', 'value': true, 'stage': -2});
        // params.push({'property': 'communicated_organ_execution', 'value': true, 'stage': 3});
        this.getGrid(cfg).setFilter(params);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getGrid(cfg),
                ]
            });
        }
        return this._formPanel;
    },

    send: function(cfg){
        var selected = this.getGrid(cfg).getSelectionModel().getSelections();
        var list = {};
        if(selected) {
            list = selected.map(
                function(data) {
                    return data.get('pk');
                }).toString();
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Remetendo dados da inspeção...'});
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                msg: 'Tem certeza que deseja remeter a inspeção ao CPJ e ao CSMP?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('INSPECTIONInspection', 'communication_cpjcsmp'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            list_inspection: list,
                        },
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                msg: 'Primeiro selecione a Inspeção/Correição que deseja remeter.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Remeter Relatório de Inspeção/Correição',
            width: 1200,
            height: 800,
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: [
                {
                    text: '<b>Remeter</b>',
                    scope: this,
                    handler: function() {
                        this.send(cfg);
                        // Ext.Msg.show({
                        //     title: 'Remeter Relatório de Inspeção/Correição',
                        //     msg: 'Em desenvolvimento...',
                        //     icon: Ext.Msg.INFO,
                        //     buttons: Ext.Msg.OK
                        // });
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        cfg.values.gridInspection.getStore().reload();
                        this.close();
                    }
                }
            ]
        });
        corregedoria.inspection.inspection.SendCommunicationCPJCSMP.superclass.constructor.call(this, cfg);
    }

});

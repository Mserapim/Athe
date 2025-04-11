Ext._define('raf.searchprocessnumber.SearchProcessNumberWindow', {
    extend: 'core.RestfulWindow',

    clear_process_number: function(value) {
        proc = value.replace(/\./g,'').replace(/\-/g,'').replace(/\//g,'');
        while (proc[0] == '0') {
            proc = proc.replace('0', '');
        }
        return proc;
    },

    pesquisar: function(cfg) {
        if (this.getFormPanel(cfg).getForm().getValues().process_number) {
            if (this.getFormPanel(cfg).getForm().getValues().source) {
                source = this.getFormPanel(cfg).getForm().getValues().source;
                proc = this.clear_process_number(this.getFormPanel(cfg).getForm().getValues().process_number);

                this.getProcessGrid().setFilterProperty('source', source, 101, false);
                this.getProcessGrid().setFilterProperty('process_number', proc, 102, true);

            } else {
                Ext.Msg.show({
                    title: 'Pesquisar por número',
                    msg: 'Selecione uma <b>ORIGEM</b> para realização da pesquisa.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Pesquisar por número',
                msg: 'Informe um <b>NÚMERO DE PROCESSO</b> para realização da pesquisa.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getProcessGrid: function() {
        if(!this._processGrid) {
            this._processGrid = Ext._create('raf.searchprocessnumber.Grid', {
                 region: 'center',
                 layout: 'fit',
                 border: false,
                 height: 500,
                 gridAutoLoad: false,
                 columnAction: false,
                 hideItemsToolbar:['add', 'edit', 'remove', 'download', '-', 'search'],
                 hiddenFilter: true,
                 doubleClickHandler: function(){},
            });
            this._processGrid.setFilterProperty('source', 0, 101, false);
            this._processGrid.setFilterProperty('process_number', 0, 102, true);
        }
        this._processGrid.enable();
        return this._processGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype:'panel',
                        autoHeight: true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 120,
                                columnWidth: 0.65,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Número do Processo',
                                        name: 'process_number',
                                        hideLabel: false,
                                        width: 560,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 45,
                                columnWidth: 0.20,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Origem',
                                        hiddenName: 'source',
                                        width: 150,
                                        choiceId: 'raf.ACTIVITY_SOURCE',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 45,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'button',
                                        text: 'Pesquisar',
                                        iconCls: 'icon-core icon-core-select',
                                        scope: this,
                                        width: 150,
                                        handler: function(cfg) { this.pesquisar(cfg); },
                                    }
                                ]
                            },
                        ]
                    },
                    this.getProcessGrid()
                ]
        });
        return this._formPanel;
    },

    getButtons: function() {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.filtered = false;
        if (cfg.hasOwnProperty("params")) {
            if (cfg.params.hasOwnProperty("process_number")) {
                this.filtered = true;
            } else {
                cfg.params.process_number = 0;
            }
        }
        Ext.applyIf(
            cfg,
            {
                title: 'Pesquisar por Número',
                modal: true,
                resizable: false,
                border: false,
                width: 1100,
                height: 605,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(cfg),
                buttons: this.getButtons(),
            }
        );
        raf.searchprocessnumber.SearchProcessNumberWindow.superclass.constructor.call(this, cfg);
        if (this.filtered) {
            this.getFormPanel(cfg).getForm().setValues({
                'process_number': cfg.params.process_number,
                'source': cfg.params.source,
            });
            // proc = this.clear_process_number(cfg.params.process_number);
            // this.getProcessGrid().setFilterProperty('source', cfg.params.source, 101, false);
            // this.getProcessGrid().setFilterProperty('process_number__icontains', proc, 102, true);
        }
    }
});

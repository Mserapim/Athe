/**
 *
 **/
Ext._define('scmmp.processojudicial.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getProcessoJudicial: function() {
        if(!this.processoJudicial) {
            this.processoJudicial = Ext._create('scmmp.processojudicial.ProcessoJudicialGrid', {
                title: 'Dados do Processo',
                region: 'center',
            });
        }

         this.processoJudicial.getSelectionModel().on({
            scope: this,
            'rowselect': function(sm, index, record) {
                this.setProcessoJudicial(record.data.pk);
            },
            'rowdeselect': function(sm) {
                this.setProcessoJudicial(null);
            }
        });

        this.processoJudicial.getStore().on({
            scope: this,
            'load': function() {
                this.setProcessoJudicial(null);
            }
        });

        this.processoJudicial.getStore().on({
            scope: this,
            'load': function() {
                var selected = (this.processoJudicial.getSelectionModel().getSelected());

                if(selected)
                    this.setProcessoJudicial(selected.get('pk'));
                else
                    this.setProcessoJudicial(null);
            }
        });

        return this.processoJudicial;
    },

    setProcessoJudicial: function(processoId) {
        this.processoId = processoId;
        this._observeProcesso();
    },

    _observeProcesso: function() {
        if(this.processoId) {
            this.getMembroProcesso().enable();
            this.getMembroProcesso().setFilterProperty('processo_judicial', this.processoId);
            this.getMembroProcesso().setParam('processo_judicial', this.processoId);
            this.getMembroProcesso().idProcesso = this.processoId;
            
            this.getFaseRecursal().enable();
            this.getFaseRecursal().setFilterProperty('processo_judicial', this.processoId);
            this.getFaseRecursal().setParam('processo_judicial', this.processoId);
            // this.getAddressGrid().idMember = this.processoId;
        }
        else {
            this.getMembroProcesso().getStore().removeAll();
            this.getMembroProcesso().disable();

            this.getFaseRecursal().getStore().removeAll();
            this.getFaseRecursal().disable();
        }
    },

    getMembroProcesso: function() {
        if(!this.membroprocesso) {
            this.membroprocesso = Ext._create('scmmp.membroprocesso.MembroProcessoGrid', {
                title: 'Membros Vinculados',
                flex: 1.0,
                border: true,
            });
        }

        return this.membroprocesso;
    },

    getFaseRecursal: function() {
        if(!this.faserecursal) {
            this.faserecursal = Ext._create('scmmp.faserecursal.FaseRecursalGrid', {
                title: 'Fase Recursal',
                region: 'south',
                flex:1,
                layout:'fit',
            });
        }

        return this.faserecursal;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Processos Judiciais'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getProcessoJudicial(),
                    {
                        'listeners': {
                            scope: this,
                            'render': function() {
                            }
                        },
                        region: 'south',
                        layout: 'hbox',
                        minHeight: 150,
                        height: 400,
                        split: true,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getMembroProcesso(),
                            this.getFaseRecursal(),
                        ]
                    }
                ]
            }
        );

        scmmp.processojudicial.Manage.superclass.constructor.call(this, cfg);
    }
});
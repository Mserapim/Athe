/**
 *
 **/
Ext._define('cif.ManageConfiguration', {
    extend: 'toolkit.widget.TabPanel',

    getCodeProperty: function() {
        if(!this.codeproperty) {
            this.codeproperty = Ext._create('cif.codeproperty.CodePropertyGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.codeproperty;
    },

    getCodeDebts: function() {
        if(!this.codedebts) {
            this.codedebts = Ext._create('cif.codedebtsencumbrances.CodeDebtsEncumbrancesGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.codedebts;
    },

    getEducational: function() {
        if(!this.educational) {
            this.educational = Ext._create('cif.educational.EducationalInstitutionGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.educational;
    },

    getDiscipline: function() {
        if(!this.discipline) {
            this.discipline = Ext._create('cif.schedule.ScheduleGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.discipline;
    },

    getSchedule: function() {
        if(!this.schedule) {
            this.schedule = Ext._create('cif.schedule.ScheduleGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.schedule;
    },

    getReferencePeriod: function() {
        if(!this.reference) {
            this.reference = Ext._create('cif.referenceperiod.ReferencePeriodGrid', {
                region: 'center',
                height: 300,
            });
        }

        return this.reference;
    },
    
    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                title: 'Gestor de Configurações',
                border: true,
                autoScroll: true,
                region: 'center',
                padding: '15',
                items: [
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Código de Bens',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getCodeProperty()
                            
                        ]
                    },
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Código de Dívida e Ônus Reais',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getCodeDebts()
                            
                        ]
                    },
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Instituição de Ensino',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getEducational()
                            
                        ]
                    },
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Disciplina',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getDiscipline()
                            
                        ]
                    },
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Horário',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getSchedule()
                            
                        ]
                    },
                    {
                        collapsible: true,
                        collapsed: true,
                        xtype: 'fieldset',
                        title: 'Período de Referência',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            this.getReferencePeriod()
                            
                        ]
                    },
                   
                ],
            });

        return this._formPanel;
    },

    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Configurações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getFormPanel(),
                ]
            }
        );

        cif.ManageConfiguration.superclass.constructor.call(this, cfg);
    }
});

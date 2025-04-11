Ext._define('corregedoria.cirdir.teaching.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.teaching.Restful',

    width: 900,

    getInstitutionField: function(cfg) {
        if(!this._institutionField) {
            this._institutionField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Instituição',
                allowBlank: true,
                rest: "corregedoria.cirdir.teaching.institution.Restful",
                name: "institution",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                }
            });
        }
        return this._institutionField;
    },

    getDisciplineField: function(cfg) {
        if(!this._disciplineField) {
            this._disciplineField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Disciplina',
                allowBlank: true,
                rest: "corregedoria.cirdir.teaching.discipline.Restful",
                name: "discipline",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                }
            });
        }
        return this._disciplineField;
    },

    getScheduleField: function(cfg) {
      if(!this._scheduleField)
          this._scheduleField = Ext._create('core.fields.RelatedRestfulField', {
            title: 'Horários',
            hideLabel: true,
            name: 'schedule',
            displayField: 'unicode',
            allowBlank: true,
            relatedname: 'in_teaching',
            rest: this.rest,
            sourceRest: 'corregedoria.cirdir.teaching.schedule.Restful',
            oId: this.oId || cfg.oId,
            width: 875,
            height: 275,
            border: false,
            gridConfig: {
                columnAction: false,
            }
          });
      return this._scheduleField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 355,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 60,
                        items: [
                            this.getInstitutionField(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 65,
                                columnWidth: 0.22,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Modalidade',
                                        hiddenName: 'modality',
                                        width: 110,
                                        choiceId: 'cirdir.MODALITY',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 60,
                                columnWidth: 0.78,
                                items: [
                                    this.getDisciplineField(cfg),
                                ]
                            },
                          ]
                      },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 82,
                                columnWidth: 0.25,
                                items: [
                                  {
                                      xtype: 'datefield',
                                      fieldLabel: 'Data de Início',
                                      width: 115,
                                      name: 'start_date',
                                  },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 95,
                                columnWidth: 0.26,
                                items: [
                                  {
                                      xtype: 'datefield',
                                      fieldLabel: 'Data de Término',
                                      width: 115,
                                      name: 'end_date',
                                  },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 78,
                                columnWidth: 0.23,
                                items: [
                                  {
                                      xtype: 'textfield',
                                      fieldLabel: 'Carga Horária',
                                      width: 105,
                                      name: 'work_hours',
                                  },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.26,
                                items: [
                                  {
                                      xtype: 'checkbox',
                                      name: 'authorization_teaching',
                                      boxLabel: 'Possui autorização do CSMP. ',
                                  },
                                ]
                            },
                          ]
                      },
                      this.getScheduleField(cfg),
                  ]
            });

        return this._formPanel;
    },

    observer: function(cfg) {
        if (this.oId) {
            this.getScheduleField(cfg).objectId(this.oId);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.observer(cfg);
                }
            }
        });
        corregedoria.cirdir.teaching.Window.superclass.constructor.call(this, cfg);
        this.observer(cfg);
    },

});

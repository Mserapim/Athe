Ext._define('corregedoria.cirdir.teaching.schedule.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.teaching.schedule.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  {
                      xtype:'panel',
                      autoHeight:true,
                      layout: 'column',
                      items: [
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 27,
                              columnWidth: 0.27,
                              items: [
                                  {
                                      xtype: 'choicefield',
                                      fieldLabel: 'Tipo',
                                      hiddenName: 'type_schedule',
                                      width: 80,
                                      choiceId: 'cirdir.TYPE_SCHEDULE',
                                      listeners: {
                                          scope: this,
                                          select: function(index){
                                              dayField = this.getFormPanel(cfg).find('hiddenName', 'day_week')[0];
                                              dateField = this.getFormPanel(cfg).find('name', 'date_module')[0];
                                              if (index.value==1) {
                                                  dayField.enable();
                                                  dateField.disable();
                                              }
                                              if (index.value==2) {
                                                  dayField.disable();
                                                  dateField.enable();
                                              }
                                          },
                                          render: function(){
                                              typeField = this.getFormPanel(cfg).find('hiddenName', 'type_schedule')[0];
                                              dayField = this.getFormPanel(cfg).find('hiddenName', 'day_week')[0];
                                              dateField = this.getFormPanel(cfg).find('name', 'date_module')[0];
                                              if (typeField.value==1) {
                                                  dayField.enable();
                                                  dateField.disable();
                                              }
                                              if (typeField.value==2) {
                                                  dayField.disable();
                                                  dateField.enable();
                                              }
                                          },
                                      }
                                  },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 85,
                              columnWidth: 0.45,
                              items: [
                                  {
                                      xtype: 'choicefield',
                                      fieldLabel: 'Dia da Semana',
                                      hiddenName: 'day_week',
                                      width: 110,
                                      choiceId: 'cirdir.DAY_WEEK',
                                      disabled: true,
                                  },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 30,
                              columnWidth: 0.28,
                              items: [
                                  {
                                      xtype: 'datefield',
                                      fieldLabel: 'Data',
                                      width: 95,
                                      name: 'date_module',
                                      disabled: true,
                                  },
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
                              labelWidth: 95,
                              columnWidth: 0.50,
                              items: [
                                  {
                                      xtype: "textfield",
                                      fieldLabel: 'Horário de Início',
                                      name: "start_time",
                                      width: 120,
                                      emptyText: 'HH:MM:SS',
                                      regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/,
                                      regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM:SS</b>.',
                                      maxLength: 8,
                                      maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM:SS</b>.',
                                      listeners: {
                                          scope: this,
                                          blur: function(){
                                              cmp = this.getFormPanel(cfg).find('name', 'start_time')[0];
                                              if (cmp.getValue().length == 2) {
                                                  cmp.setValue(cmp.getValue()+':00:00');
                                              }
                                              if (cmp.getValue().length == 5) {
                                                  cmp.setValue(cmp.getValue()+':00');
                                              }
                                          },
                                      },
                                  },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 110,
                              columnWidth: 0.50,
                              items: [
                                  {
                                      xtype: "textfield",
                                      fieldLabel: 'Horário de Término',
                                      name: "end_time",
                                      width: 120,
                                      emptyText: 'HH:MM:SS',
                                      regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/,
                                      regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM:SS</b>.',
                                      maxLength: 8,
                                      maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM:SS</b>.',
                                      listeners: {
                                          scope: this,
                                          blur: function(){
                                              cmp = this.getFormPanel(cfg).find('name', 'end_time')[0];
                                              if (cmp.getValue().length == 2) {
                                                  cmp.setValue(cmp.getValue()+':00:00');
                                              }
                                              if (cmp.getValue().length == 5) {
                                                  cmp.setValue(cmp.getValue()+':00');
                                              }
                                          },
                                      },
                                  },
                              ]
                          },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
        });
        corregedoria.cirdir.teaching.schedule.Window.superclass.constructor.call(this, cfg);
    },

});
